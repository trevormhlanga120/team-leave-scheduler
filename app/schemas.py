from datetime import date
from pydantic import BaseModel
from .models import LeaveStatus


class EmployeeOut(BaseModel):
    id: int
    name: str
    team_id: int

    class Config:
        from_attributes = True


class LeaveRequestCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date


class LeaveRequestOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    team_id: int
    start_date: date
    end_date: date
    status: LeaveStatus

    class Config:
        from_attributes = True