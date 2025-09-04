from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from utils.db import Base

class Permission(Base):
    __tablename__ = "Permission"

    Permission_Id = Column(Integer, primary_key=True, autoincrement=True)
    Employee_Id = Column(Integer, nullable=False)
    Company = Column(String(100), nullable=False)
    Created_At = Column(DateTime, server_default=func.now(), nullable=False)
    Valid_Until = Column(DateTime, nullable=False)
    Is_Active = Column(Boolean, nullable=False, default=True)
