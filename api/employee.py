from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.employee import EmployeeBase
from models.employee import Employee
from utils.payroll_db import get_db as get_payroll_db
from utils.photo_utils import photo_to_base64

router = APIRouter()

@router.get("/{id_empleado}", response_model=EmployeeBase)
def get_empleados(
    id_empleado: int,
    payroll_db: Session = Depends(get_payroll_db),
):
    empleado = payroll_db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    return EmployeeBase(
        Employee_Id=id_empleado,
        Name=empleado.NombreCompleto if empleado else "Desconocido",
        Photo=photo_to_base64(empleado.Foto) if empleado else None
    )
