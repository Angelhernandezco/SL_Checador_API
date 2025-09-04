from sqlalchemy import Column, Integer, String, DateTime
from config.settings import settings
from utils.db import Base

class ExitRecord(Base):
    __tablename__ = "Exit_Record"

    Exit_Record_Id = Column(Integer, primary_key=True, autoincrement=True)
    Employee_Id = Column(Integer, nullable=False)
    Company = Column(String(100), nullable=False)
    DateHour = Column(DateTime, nullable=False)
    Exit_Type = Column(String(3), nullable=False)
