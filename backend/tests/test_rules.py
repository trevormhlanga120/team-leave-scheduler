import sys
from pathlib import Path
from datetime import date

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi import HTTPException
from app.database import Base
from app import models, rules
from app.routers.leave import approve_leave
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def make_team_of(db, size):
    team = models.Team(name="Engineering")
    db.add(team)
    db.flush()
    employees = []
    for i in range(size):
        e = models.Employee(name=f"Emp{i}", team_id=team.id)
        db.add(e)
        employees.append(e)
    db.commit()
    return employees


def test_30_percent_cap_blocks_4th_person_on_team_of_10(db):
    employees = make_team_of(db, 10)  # cap = floor(10*0.3) = 3
    day = date(2026, 7, 6)  # a Monday, no holiday
    for e in employees[:3]:
        db.add(models.LeaveRequest(
            employee_id=e.id, start_date=day, end_date=day,
            status=models.LeaveStatus.APPROVED,
        ))
    db.commit()

    breaching = rules.violates_team_cap(db, employees[3].id, day, day)
    assert breaching == [day]


def test_overlap_rejects_request_overlapping_approved_leave(db):
    employees = make_team_of(db, 5)
    e = employees[0]
    db.add(models.LeaveRequest(
        employee_id=e.id,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 5),
        status=models.LeaveStatus.APPROVED,
    ))
    db.commit()

    assert rules.has_overlapping_approved_leave(db, e.id, date(2026, 7, 4), date(2026, 7, 8)) is True
    assert rules.has_overlapping_approved_leave(db, e.id, date(2026, 7, 10), date(2026, 7, 12)) is False


def test_overlap_check_can_exclude_current_request(db):
    employees = make_team_of(db, 5)
    e = employees[0]
    existing = models.LeaveRequest(
        employee_id=e.id,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 5),
        status=models.LeaveStatus.APPROVED,
    )
    db.add(existing)
    db.commit()

    assert rules.has_overlapping_approved_leave(
        db,
        e.id,
        date(2026, 7, 1),
        date(2026, 7, 5),
        exclude_request_id=existing.id,
    ) is False


def test_public_holiday_is_ignored_for_team_cap(db):
    employees = make_team_of(db, 4)  # cap = floor(4*0.3) = 1
    holiday = date(2026, 8, 11)
    db.add(models.PublicHoliday(date=holiday, name="Test Holiday"))
    db.add(
        models.LeaveRequest(
            employee_id=employees[0].id,
            start_date=holiday,
            end_date=holiday,
            status=models.LeaveStatus.APPROVED,
        )
    )
    db.commit()

    assert rules.violates_team_cap(db, employees[1].id, holiday, holiday) == []


def test_approval_rechecks_overlap_against_approved_leave(db):
    employees = make_team_of(db, 5)
    e = employees[0]
    approved = models.LeaveRequest(
        employee_id=e.id,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 3),
        status=models.LeaveStatus.APPROVED,
    )
    pending = models.LeaveRequest(
        employee_id=e.id,
        start_date=date(2026, 7, 2),
        end_date=date(2026, 7, 4),
        status=models.LeaveStatus.PENDING,
    )
    db.add_all([approved, pending])
    db.commit()

    with pytest.raises(HTTPException) as exc:
        approve_leave(pending.id, db)

    assert exc.value.status_code == 409
    assert "overlaps" in exc.value.detail
