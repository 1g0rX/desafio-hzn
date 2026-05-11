# models.py
from sqlalchemy import Column, Integer, String, Text
from database import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)

    # proponent data
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    file_path = Column(String)

    # AI generated data
    score = Column(String, nullable=True)
    verdict = Column(String, nullable=True)
    red_flags = Column(Text, nullable=True)
    opportunity_cost = Column(Text, nullable=True)

    # flow control
    status = Column(String, default="UNDER_ANALYSIS") # UNDER_ANALYSIS, APPROVED, REJECTED