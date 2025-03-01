from src.database.connect_db import get_db
from src.models.meta_table_model import MetaTable
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

router = APIRouter()

nested_dict = {"By_Product": {}}

@router.get("/tables/{id}")
async def get_table(id: int, db: Session = Depends(get_db)):
    """Fetch table data and unique regions from the given table ID."""
    
    # Fetch table metadata
    table = db.query(MetaTable).filter(MetaTable.id == id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table_name = table.table_name

    try:
        segment_data = extract_unique_segment_subsegment(db, table_name)
        
        return {"Data": segment_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def fetch_table_data(db: Session, table_name: str):
    """Fetch all data from the given table and return as a list of dictionaries."""
    query = text(f"SELECT * FROM {table_name}")
    result = db.execute(query)
    
    columns = result.keys()  # Extract column names
    return [dict(zip(columns, row)) for row in result.fetchall()]


def extract_unique_regions(db: Session, table_name: str):
    query = text(f"SELECT DISTINCT region FROM {table_name}")
    result = db.execute(query)
    
    return [row[0] for row in result.fetchall()]

def extract_unique_segment_subsegment(db: Session, table_name: str):
    query = text(f"SELECT segment, sub_segment, sub_segment1 FROM {table_name}")
    result = db.execute(query)

    # Fetch all rows and get column names
    rows = result.fetchall()
    columns = result.keys()

    # Convert rows into a list of dictionaries
    data = [dict(zip(columns, row)) for row in rows]
    return data


