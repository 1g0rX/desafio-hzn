from pydantic import BaseModel
from typing import Optional

# scheme for the return of the data

class OportunidadeResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    score: Optional[str] = None
    veredict: Optional[str] = None
    red_flags: Optional[str] = None
    cost_opportunity: Optional[str] = None
    status: str

    class Config:
        from_attributes: True

 