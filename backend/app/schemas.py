from datetime import date
from pydantic import BaseModel, ConfigDict
from .models import LeaveStatus


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    team_id: int


class LeaveRequestCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date


class LeaveRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    employee_name: str
    team_id: int
    start_date: date
    end_date: date
    status: LeaveStatus
