import sys
from pathlib import Path
from datetime import date

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from app.database import Base
from app import models, rules
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