from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database, rules

router = APIRouter(prefix="/leave", tags=["leave"])


def _to_out(r: models.LeaveRequest) -> schemas.LeaveRequestOut:
    return schemas.LeaveRequestOut(
        id=r.id,
        employee_id=r.employee_id,
        employee_name=r.employee.name,
        team_id=r.employee.team_id,
        start_date=r.start_date,
        end_date=r.end_date,
        status=r.status,
    )


@router.get("/", response_model=list[schemas.LeaveRequestOut])
def list_leave(days: int = 30, db: Session = Depends(database.get_db)):
    """Leave requests overlapping the next `days` days."""
    today = date.today()
    horizon = today + timedelta(days=days)
    requests = (
        db.query(models.LeaveRequest)
        .filter(models.LeaveRequest.start_date <= horizon, models.LeaveRequest.end_date >= today)
        .all()
    )
    return [_to_out(r) for r in requests]


@router.post("/", response_model=schemas.LeaveRequestOut)
def submit_leave(payload: schemas.LeaveRequestCreate, db: Session = Depends(database.get_db)):
    if payload.end_date < payload.start_date:
        raise HTTPException(400, "end_date must not be before start_date")

    employee = db.query(models.Employee).filter(models.Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(404, "Employee not found")

    if rules.has_overlapping_approved_leave(db, payload.employee_id, payload.start_date, payload.end_date):
        raise HTTPException(409, "Request overlaps an existing approved leave for this employee")

    leave_request = models.LeaveRequest(
        employee_id=payload.employee_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=models.LeaveStatus.PENDING,
    )
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    return _to_out(leave_request)


@router.put("/{request_id}/approve", response_model=schemas.LeaveRequestOut)
def approve_leave(request_id: int, db: Session = Depends(database.get_db)):
    leave_request = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not leave_request:
        raise HTTPException(404, "Leave request not found")

    breaching_days = rules.violates_team_cap(
        db, leave_request.employee_id, leave_request.start_date, leave_request.end_date
    )
    if breaching_days:
        raise HTTPException(
            409,
            f"Approving this would breach the 30% team cap on: "
            f"{', '.join(d.isoformat() for d in breaching_days)}",
        )

    leave_request.status = models.LeaveStatus.APPROVED
    db.commit()
    db.refresh(leave_request)
    return _to_out(leave_request)


@router.put("/{request_id}/reject", response_model=schemas.LeaveRequestOut)
def reject_leave(request_id: int, db: Session = Depends(database.get_db)):
    leave_request = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not leave_request:
        raise HTTPException(404, "Leave request not found")

    leave_request.status = models.LeaveStatus.REJECTED
    db.commit()
    db.refresh(leave_request)
    return _to_out(leave_request)

