from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .database import Base


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    employees = relationship("Employee", back_populates="team")


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    team = relationship("Team", back_populates="employees")
    leave_requests = relationship("LeaveRequest", back_populates="employee")


class PublicHoliday(Base):
    __tablename__ = "public_holidays"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    name = Column(String, nullable=False)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)

    employee = relationship("Employee", back_populates="leave_requests")