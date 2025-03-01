from sqlalchemy import Column, Integer, String, DateTime, func
from src.database.connect_db import Base

class MetaTable(Base):
    __tablename__ = "meta_table"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, unique=True, nullable=False)
    region = Column(String)
    segment_subsegment = Column(String)
    start_year = Column(Integer)
    end_year = Column(Integer)

    created_at = Column(DateTime, default=func.now())