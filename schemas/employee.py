from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    Employee_Id: int
    Name: str
    Photo: Optional[str] = None

    model_config = {
        "from_attributes": True
    }