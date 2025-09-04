from sqlalchemy import Column, Integer, String, LargeBinary
from utils.payroll_db import Base


class Employee(Base):
    __tablename__ = "Empleado"

    ID_Empleado = Column(Integer, primary_key=True, autoincrement=True)
    NombreCompleto = Column(String(100), nullable=False)
    Foto = Column(LargeBinary, nullable=True)
