from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from schemas.employee import EmployeeBase
from utils.db import get_db
from models.exit_record import ExitRecord
from models.permission import Permission
from models.employee import Employee
from openpyxl import Workbook
from datetime import datetime, date
import io

router = APIRouter()


# -------------------------------
# Registrar salida de empleado
# -------------------------------
@router.get("/out/{id_empleado}")
def registrar_salida(id_empleado: int, db: Session = Depends(get_db)):
    ahora = datetime.now()

    # Verificar que el empleado tenga un permiso válido y activo
    permiso = (
        db.query(Permission)
        .filter(
            Permission.Employee_Id == id_empleado,
            Permission.Is_Active == True,
            Permission.Valid_Until >= ahora,
        )
        .first()
    )
    if not permiso:
        raise HTTPException(status_code=403, detail="Empleado no tiene permiso válido hoy")

    # Validar que no tenga ya un OUT sin IN
    last_record = (
        db.query(ExitRecord)
        .filter_by(Employee_Id=id_empleado)
        .order_by(ExitRecord.DateHour.desc())
        .first()
    )
    if last_record and last_record.Exit_Type == "OUT":
        raise HTTPException(status_code=400, detail="Empleado ya salió y no ha regresado")

    # Insertar salida
    salida = ExitRecord(
        Employee_Id=id_empleado,
        Name="",  # opcional, si lo llenas desde Employee
        DateHour=ahora,
        Exit_Type="OUT",
    )
    db.add(salida)
    db.commit()
    db.refresh(salida)

    empleado = db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    return EmployeeBase(
        Employee_Id=id_empleado,
        Name=empleado.nombre if empleado else "Desconocido",
        Photo=empleado.foto if empleado else None,
    )


# -------------------------------
# Registrar entrada
# -------------------------------
@router.post("/in/{id_empleado}")
def registrar_entrada(id_empleado: int, db: Session = Depends(get_db)):
    last_record = (
        db.query(ExitRecord)
        .filter_by(Employee_Id=id_empleado)
        .order_by(ExitRecord.DateHour.desc())
        .first()
    )

    if not last_record or last_record.Exit_Type != "OUT":
        raise HTTPException(status_code=400, detail="Empleado no tiene salida pendiente")

    entrada = ExitRecord(
        Employee_Id=id_empleado,
        Name="",
        DateHour=datetime.now(),
        Exit_Type="IN",
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)

    empleado = db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    return EmployeeBase(
        Employee_Id=id_empleado,
        Name=empleado.nombre if empleado else "Desconocido",
        Photo=empleado.foto if empleado else None,
    )


# -------------------------------
# Reporte de ausentes en rango
# -------------------------------
@router.get("/missing-report")
def reporte_ausentes(fecha_inicio: str, fecha_fin: str, db: Session = Depends(get_db)):
    fi = datetime.fromisoformat(fecha_inicio)
    ff = datetime.fromisoformat(fecha_fin)

    # Traer permisos activos dentro del rango
    permisos = (
        db.query(Permission)
        .filter(
            Permission.Created_At >= fi,
            Permission.Created_At <= ff,
            Permission.Is_Active == True,
        )
        .all()
    )

    ausentes = []
    for permiso in permisos:
        salida = (
            db.query(ExitRecord)
            .filter(
                ExitRecord.Employee_Id == permiso.Employee_Id,
                ExitRecord.Exit_Type == "OUT",
                ExitRecord.DateHour >= permiso.Created_At,
                ExitRecord.DateHour <= permiso.Valid_Until,
            )
            .order_by(ExitRecord.DateHour.desc())
            .first()
        )
        if salida:
            entrada = (
                db.query(ExitRecord)
                .filter(
                    ExitRecord.Employee_Id == permiso.Employee_Id,
                    ExitRecord.Exit_Type == "IN",
                    ExitRecord.DateHour > salida.DateHour,
                )
                .first()
            )
            if not entrada:
                ausentes.append(salida)

    # Crear Excel
    wb = Workbook()
    ws = wb.active
    ws.append(["Empleado", "Nombre", "Fecha salida"])
    for r in ausentes:
        ws.append([r.Employee_Id, r.Name, r.DateHour.isoformat()])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=reporte.xlsx"},
    )
