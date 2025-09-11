from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from schemas.employee import EmployeeBase
from utils.payroll_db import get_db as get_db_payroll
from utils.db import get_db
from models.exit_record import ExitRecord
from models.permission import Permission
from models.employee import Employee
from openpyxl import Workbook
from datetime import datetime, time
import io

from utils.photo_utils import photo_to_base64

router = APIRouter()


# -------------------------------
# Registrar salida de empleado
# -------------------------------
@router.get("/out/{id_empleado}")
def registrar_salida(id_empleado: int, db: Session = Depends(get_db), payroll_db: Session = Depends(get_db_payroll)):
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
        raise HTTPException(status_code=400, detail="Empleado ya salió y no ha regresado hoy")

    # Insertar salida
    salida = ExitRecord(
        Employee_Id=id_empleado,
        Company="Empaque",
        DateHour=ahora,
        Exit_Type="OUT",
    )
    db.add(salida)
    db.commit()
    db.refresh(salida)

    empleado = payroll_db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    return EmployeeBase(
        Employee_Id=id_empleado,
        Name=empleado.NombreCompleto if empleado else "Desconocido",
        Photo=photo_to_base64(empleado.Foto) if empleado else None
    )


# -------------------------------
# Registrar entrada
# -------------------------------
@router.post("/in/{id_empleado}")
def registrar_entrada(id_empleado: int, db: Session = Depends(get_db), payroll_db: Session = Depends(get_db_payroll)):
    ahora = datetime.now()
    inicio_dia = datetime.combine(ahora.date(), time.min)  # 00:00:00
    fin_dia = datetime.combine(ahora.date(), time.max)  # 23:59:59.999999

    # Buscar el último registro del día
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

    if not last_record or last_record.Exit_Type != "OUT":
        raise HTTPException(status_code=400, detail="Empleado no tiene salida pendiente")

    entrada = ExitRecord(
        Employee_Id=id_empleado,
        Company="Empaque",
        DateHour=ahora,
        Exit_Type="IN",
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)

    empleado = payroll_db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    return EmployeeBase(
        Employee_Id=id_empleado,
        Name=empleado.NombreCompleto if empleado else "Desconocido",
        Photo=photo_to_base64(empleado.Foto) if empleado else None
    )


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from schemas.employee import EmployeeBase
from utils.payroll_db import get_db as get_db_payroll
from utils.db import get_db
from models.exit_record import ExitRecord
from models.permission import Permission
from models.employee import Employee
from openpyxl import Workbook
from datetime import datetime, time
import io

from utils.photo_utils import photo_to_base64

router = APIRouter()


# -------------------------------
# Registrar salida de empleado
# -------------------------------
@router.post("/out/{id_empleado}")
def registrar_salida(id_empleado: int, db: Session = Depends(get_db), payroll_db: Session = Depends(get_db_payroll)):
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
        raise HTTPException(status_code=400, detail="Empleado ya salió y no ha regresado hoy")

    # Insertar salida
    salida = ExitRecord(
        Employee_Id=id_empleado,
        Company="Empaque",
        DateHour=ahora,
        Exit_Type="OUT",
    )
    db.add(salida)
    db.commit()
    db.refresh(salida)

    empleado = payroll_db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    return EmployeeBase(
        Employee_Id=id_empleado,
        Name=empleado.NombreCompleto if empleado else "Desconocido",
        Photo=photo_to_base64(empleado.Foto) if empleado else None
    )


# -------------------------------
# Registrar entrada
# -------------------------------
@router.post("/in/{id_empleado}")
def registrar_entrada(id_empleado: int, db: Session = Depends(get_db), payroll_db: Session = Depends(get_db_payroll)):
    ahora = datetime.now()
    inicio_dia = datetime.combine(ahora.date(), time.min)  # 00:00:00
    fin_dia = datetime.combine(ahora.date(), time.max)  # 23:59:59.999999

    # Buscar el último registro del día
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

    if not last_record or last_record.Exit_Type != "OUT":
        raise HTTPException(status_code=400, detail="Empleado no tiene salida pendiente")

    entrada = ExitRecord(
        Employee_Id=id_empleado,
        Company="Empaque",
        DateHour=ahora,
        Exit_Type="IN",
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)

    empleado = payroll_db.query(Employee).filter_by(ID_Empleado=id_empleado).first()
    return EmployeeBase(
        Employee_Id=id_empleado,
        Name=empleado.NombreCompleto if empleado else "Desconocido",
        Photo=photo_to_base64(empleado.Foto) if empleado else None
    )


# -------------------------------
# Reporte de ausentes por rango
# -------------------------------
@router.get("/missing-report")
def reporte_ausentes(fecha_inicio: str, fecha_fin: str, db: Session = Depends(get_db), payroll_db: Session = Depends(get_db_payroll)):
    fi = datetime.fromisoformat(fecha_inicio)
    ff = datetime.fromisoformat(fecha_fin)

    # Traer todas las salidas (OUT) dentro del rango
    salidas = (
        db.query(ExitRecord)
        .filter(
            ExitRecord.Exit_Type == "OUT",
            ExitRecord.DateHour >= fi,
            ExitRecord.DateHour <= ff,
        )
        .order_by(ExitRecord.Employee_Id, ExitRecord.DateHour)
        .all()
    )

    ausentes = []

    for salida in salidas:
        # Definir inicio y fin del día de la salida
        inicio_dia = datetime.combine(salida.DateHour.date(), time.min)
        fin_dia = datetime.combine(salida.DateHour.date(), time.max)

        # Verificar si hay una entrada (IN) ese mismo día, posterior a la salida
        entrada = (
            db.query(ExitRecord)
            .filter(
                ExitRecord.Employee_Id == salida.Employee_Id,
                ExitRecord.Exit_Type == "IN",
                ExitRecord.DateHour >= salida.DateHour,
                ExitRecord.DateHour <= fin_dia,
            )
            .order_by(ExitRecord.DateHour)
            .first()
        )

        # Si no hay entrada ese mismo día, el empleado está ausente
        if not entrada:
            empleado = payroll_db.query(Employee).filter_by(ID_Empleado=salida.Employee_Id).first()
            ausentes.append({
                "Employee_Id": salida.Employee_Id,
                "Name": empleado.NombreCompleto if empleado else "Desconocido",
                "Photo": photo_to_base64(empleado.Foto) if empleado else None,
                "Last_Out": salida.DateHour
            })

    # Crear Excel
    wb = Workbook()
    ws = wb.active
    ws.append(["Empleado", "Nombre", "Fecha salida"])
    for r in ausentes:
        ws.append([r["Employee_Id"], r["Name"], r["Last_Out"].isoformat()])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=reporte.xlsx"},
    )
