from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import cast, String
import base64

from schemas.employee import EmployeeBase
from utils.payroll_db import get_db as get_payroll_db
from models.employee import Employee
from utils.photo_utils import photo_to_base64

router = APIRouter()

@router.get("/empleados", response_model=List[EmployeeBase])
def get_empleados(
    skip: int = 0,
    limit: int = 20,
    id_empleado: Optional[int] = None,
    nombre: Optional[str] = None,
    db: Session = Depends(get_payroll_db),
):
    query = db.query(Employee)

    if id_empleado:
        query = query.filter(cast(Employee.ID_Empleado, String).ilike(f"%{id_empleado}%"))
    if nombre:
        query = query.filter(Employee.NombreCompleto.ilike(f"%{nombre}%"))

    # Selecciona solo los campos necesarios y asigna alias para Pydantic
    empleados = (
        query.with_entities(
            Employee.ID_Empleado.label("Employee_Id"),
            Employee.NombreCompleto.label("Name"),
            Employee.Foto.label("Photo")
        )
        .order_by(Employee.ID_Empleado)
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = [
        {
            "Employee_Id": e.Employee_Id,
            "Name": e.Name,
            "Photo": photo_to_base64(e.Photo)
        }
        for e in empleados
    ]

    return result
