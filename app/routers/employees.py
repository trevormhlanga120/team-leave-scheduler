from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/", response_model=list[schemas.EmployeeOut])
def list_employees(db: Session = Depends(database.get_db)):
    return db.query(models.Employee).all()