from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from schemas.employee import EmployeeBase


class PermissionBase(BaseModel):
    Employee_Id: int
    Company: str
    Valid_Until: datetime
    Is_Active: bool


class PermissionWithEmployee(EmployeeBase):
    Company: str
    Valid_Until: datetime

    model_config = {
        "from_attributes": True
    }

