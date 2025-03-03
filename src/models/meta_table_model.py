from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from src.database.connect_db import Base

class MetaTable(Base):
    __tablename__ = "meta_table"

    id = Column(String, primary_key=True, index=True)
    table_name = Column(String, unique=True, nullable=False)
    region = Column(String)
    segment_subsegment = Column(JSON)
    start_year = Column(Integer)
    end_year = Column(Integer)
    created_at = Column(DateTime, default=func.now())