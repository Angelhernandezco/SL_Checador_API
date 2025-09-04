from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# -------------------------------
# Modelo base de permiso
# -------------------------------
class PermissionBase(BaseModel):
    Employee_Id: int
    Company: str
    Valid_Until: datetime
    Is_Active: bool


class PermissionWithEmployee(BaseModel):
    Employee_Id: int
    Name: str
    Photo: Optional[str]
    Company: str
    Valid_Until: datetime

    class Config:
        orm_mode = True

