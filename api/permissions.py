from typing import List

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import Session
from models.employee import Employee
from models.exit_record import ExitRecord
from models.permission import Permission
from schemas.permission import PermissionWithEmployee
from utils.db import get_db
from utils.payroll_db import get_db as get_db_payroll
from utils.photo_utils import photo_to_base64

router = APIRouter()

# -------------------------------
# Obtener permisos del día
# -------------------------------
@router.get("/", response_model=List[PermissionWithEmployee])
def obtener_permisos(
        db: Session = Depends(get_db),
        payroll_db: Session = Depends(get_db_payroll)
):
    hoy = datetime.now()

    permisos = (
        db.query(Permission)
        .filter(Permission.Valid_Until >= hoy, Permission.Is_Active == True)
        .all()
    )

    results = []
    for permiso in permisos:
        empleado = payroll_db.query(Employee).filter_by(ID_Empleado=permiso.Employee_Id).first()
        results.append(
            PermissionWithEmployee(
                Employee_Id=permiso.Employee_Id,
                Name=empleado.NombreCompleto if empleado else "Desconocido",
                Photo=photo_to_base64(empleado.Foto) if empleado else None,
                Company=permiso.Company,
                Valid_Until=permiso.Valid_Until,
            )
        )

    return results

# -------------------------------
# Verificar si un empleado tiene permiso activo
# -------------------------------
@router.get("/{id_empleado}", response_model=PermissionWithEmployee)
def verificar_permiso(
    id_empleado: int,
    db: Session = Depends(get_db),
    payroll_db: Session = Depends(get_db_payroll),
):
    ahora = datetime.now()

    permiso = (
        db.query(Permission)
        .filter(
            Permission.Employee_Id == id_empleado,
            Permission.Is_Active == True,
            Permission.Valid_Until > ahora
        )
        .first()
    )

    if not permiso:
        raise HTTPException(status_code=404, detail="El empleado no tiene permiso activo")

    empleado = payroll_db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    return PermissionWithEmployee(
        Employee_Id=permiso.Employee_Id,
        Name=empleado.NombreCompleto if empleado else "Desconocido",
        Photo=photo_to_base64(empleado.Foto) if empleado else None,
        Company=permiso.Company,
        Valid_Until=permiso.Valid_Until,
    )


# -------------------------------
# Asignar permiso a un solo empleado y devolver datos del usuario
# -------------------------------
@router.post("/{id_empleado}", response_model=PermissionWithEmployee)
def asignar_permiso(
    id_empleado: int,
    db: Session = Depends(get_db),
    payroll_db: Session = Depends(get_db_payroll),
):
    # Buscar empleado en la nómina
    empleado = payroll_db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado en la base de datos de nómina")

    ahora = datetime.now()
    fin_dia = datetime.combine(ahora.date(), datetime.max.time())

    # Verificar si ya tiene permiso activo hoy
    permiso_existente = (
        db.query(Permission)
        .filter(
            Permission.Employee_Id == id_empleado,
            Permission.Is_Active == True,
            Permission.Valid_Until > ahora  # cualquier permiso que no haya expirado antes de hoy
        )
        .first()
    )
    if permiso_existente:
        raise HTTPException(status_code=400, detail="El empleado ya tiene un permiso asignado")

    # Crear nuevo permiso
    permiso = Permission(
        Employee_Id=id_empleado,
        Company="Empaque",
        Valid_Until=fin_dia,
        Is_Active=True,
    )
    db.add(permiso)
    db.commit()
    db.refresh(permiso)

    return PermissionWithEmployee(
        Employee_Id=empleado.ID_Empleado,
        Name=empleado.NombreCompleto,
        Photo=photo_to_base64(empleado.Foto),
        Company=permiso.Company,
        Valid_Until=permiso.Valid_Until
    )


# -------------------------------
# Quitar permiso de un solo empleado
# -------------------------------
@router.delete("/{id_empleado}")
def quitar_permiso(
    id_empleado: int,
    db: Session = Depends(get_db),
):
    ahora = datetime.now()

    inicio_dia = datetime.combine(ahora.date(), time.min)  # 00:00:00
    fin_dia = datetime.combine(ahora.date(), time.max)  # 23:59:59.999999

    # Validar que no tenga ya un OUT sin IN
    last_record = (
        db.query(ExitRecord)
        .filter(
            ExitRecord.Employee_Id == id_empleado,
            ExitRecord.DateHour >= inicio_dia,
            ExitRecord.DateHour <= fin_dia,
        )
        .order_by(ExitRecord.DateHour.desc())
        .first()
    )

    if last_record and last_record.Exit_Type == "OUT":
        raise HTTPException(status_code=400, detail="El empleado ya salió y no ha regresado")

    permiso = (
        db.query(Permission)
        .filter(
            Permission.Employee_Id == id_empleado,
            Permission.Valid_Until >= ahora,
            Permission.Is_Active == True,
        )
        .first()
    )

    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado para este empleado")

    permiso.Is_Active = False
    db.commit()

    return {"message": f"Permiso eliminado para el empleado {id_empleado}"}
