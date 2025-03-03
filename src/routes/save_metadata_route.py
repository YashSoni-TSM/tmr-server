from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.models.meta_table_model import MetaTable
from src.services.db_operations import (
    extract_unique_values, extract_columns_like, create_nested_segment
)
from src.utils.utils import split_date

router = APIRouter()

@router.get("/tables/{id}")
async def get_table(id: int, db: Session = Depends(get_db)):
    """
    Fetches table details by ID, including computed fields like regions, 
    segment-subsegment hierarchy, and date range.

    Args:
        id (int): The table ID.
        db (Session): Database session dependency.

    Returns:
        dict: Table metadata including computed values.
    """
    table = db.query(MetaTable).filter(MetaTable.id == id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table_name = table.table_name

    try:
        # Extract computed metadata
        regions = extract_unique_values(db, table_name, "region")
        segment_columns = extract_columns_like(db, table_name, "segment")
        segment_subsegment = create_nested_segment(segment_columns, table_name, db)
        
        date_columns = extract_columns_like(db, table_name, "year")
        start_year, end_year = map(split_date, [date_columns[0], date_columns[-1]])

        # Convert table object to dictionary and append computed fields
        table_data = jsonable_encoder(table)
        table_data.update({
            "region": regions,
            "segment_subsegment": segment_subsegment,
            "start_year": start_year,
            "end_year": end_year
        })

        return table_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
