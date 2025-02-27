from sqlalchemy import Column, Integer, String, DateTime, func
from src.database.connect_db import Base

class MetaTable(Base):
    __tablename__ = "meta_table"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, unique=True, nullable=False)
    segment_subsegment = Column(String)
    created_at = Column(DateTime, default=func.now())