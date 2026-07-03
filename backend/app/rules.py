from datetime import date, timedelta
from sqlalchemy.orm import Session
from . import models

# --- Documented interpretation (see DECISIONS.md) ---
# - 30% cap rounds DOWN (floor) and applies PER WORKING DAY, not to the whole range.
# - Weekends (Sat/Sun) are never counted as leave days or working days.
# - Public holidays are excluded from both leave balance and the 30% headcount for that day.
# - Overlap is checked only against APPROVED requests for the same employee.
# - The 30% denominator is the team's total headcount.


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5  # 5=Saturday, 6=Sunday


def get_holiday_dates(db: Session) -> set[date]:
    return {h.date for h in db.query(models.PublicHoliday).all()}


def working_days_in_range(start: date, end: date, holidays: set[date]) -> list[date]:
    days = []
    current = start
    while current <= end:
        if not is_weekend(current) and current not in holidays:
            days.append(current)
        current += timedelta(days=1)
    return days


def overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return a_start <= b_end and b_start <= a_end


def has_overlapping_approved_leave(
    db: Session,
    employee_id: int,
    start: date,
    end: date,
    exclude_request_id: int | None = None,
) -> bool:
    query = (
        db.query(models.LeaveRequest)
        .filter(
            models.LeaveRequest.employee_id == employee_id,
            models.LeaveRequest.status == models.LeaveStatus.APPROVED,
        )
    )

    if exclude_request_id is not None:
        query = query.filter(models.LeaveRequest.id != exclude_request_id)

    approved = query.all()
    return any(overlaps(start, end, r.start_date, r.end_date) for r in approved)


def team_leave_cap(team_size: int) -> int:
    """Max employees allowed on leave on a given day. Rounds down."""
    return int(team_size * 0.3)


def violates_team_cap(
    db: Session,
    employee_id: int,
    start: date,
    end: date,
    exclude_request_id: int | None = None,
) -> list[date]:
    """Returns the list of working days on which approving this request would
    push the team over its 30% cap. Empty list means the request is safe."""
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    team_id = employee.team_id
    team_size = db.query(models.Employee).filter(models.Employee.team_id == team_id).count()
    cap = team_leave_cap(team_size)

    holidays = get_holiday_dates(db)
    days_to_check = working_days_in_range(start, end, holidays)

    breaching_days = []
    for day in days_to_check:
        approved_on_day = (
            db.query(models.LeaveRequest)
            .join(models.Employee)
            .filter(
                models.Employee.team_id == team_id,
                models.LeaveRequest.status == models.LeaveStatus.APPROVED,
                models.LeaveRequest.start_date <= day,
                models.LeaveRequest.end_date >= day,
            )
        )
        if exclude_request_id is not None:
            approved_on_day = approved_on_day.filter(models.LeaveRequest.id != exclude_request_id)

        approved_on_day = approved_on_day.count()
        if approved_on_day + 1 > cap:
            breaching_days.append(day)

    return breaching_days
