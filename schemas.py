# schemas.py
from pydantic import BaseModel
from typing import Optional

# Scheme for the return of the data
class OpportunityResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    score: Optional[str] = None
    verdict: Optional[str] = None
    red_flags: Optional[str] = None
    opportunity_cost: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

# Scheme for the evaluator decision payload
class EvaluatorDecision(BaseModel):
    decision: str # "APPROVED" or "REJECTED"