import csv
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from . import models

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def seed(db: Session):
    if db.query(models.Team).first():
        return  # already seeded

    teams_cache = {}

    with open(DATA_DIR / "employees.csv") as f:
        reader = csv.DictReader(f)

        for row in reader:
            team_name = row["team"]

            if team_name not in teams_cache:
                team = models.Team(name=team_name)
                db.add(team)
                db.flush()  # get team.id without committing
                teams_cache[team_name] = team

            db.add(
                models.Employee(
                    name=row["name"],
                    team_id=teams_cache[team_name].id,
                )
            )

    with open(DATA_DIR / "public_holidays.json") as f:
        holidays = json.load(f)

        for h in holidays:
            db.add(
                models.PublicHoliday(
                    date=datetime.strptime(h["date"], "%Y-%m-%d").date(),
                    name=h["name"],
                )
            )

    db.commit()