from fastapi import UploadFile, File, Depends, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd
from src.database.connect_db import get_db
from src.services.excel_processor import process_excel_file
from src.services.db_operations import create_table, bulk_insert_using_copy

router = APIRouter()

@router.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = process_excel_file(file)

    if df is None:
        return {"error": "The uploaded file contains no valid data"}

    # Generate a unique table name
    table_name = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Create a table dynamically
    create_table(df, table_name, db)

    # Perform bulk insert
    bulk_insert_using_copy(df, table_name, db)

    return {"message": "Data uploaded successfully", "table_name": table_name}
