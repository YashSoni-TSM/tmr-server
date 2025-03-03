from fastapi import UploadFile, File, Depends, APIRouter
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.services.excel_processor import process_excel_file
from src.services.db_operations import create_table, bulk_insert_using_copy

router = APIRouter()

@router.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Handles the uploading and processing of an Excel file.
    
    Steps:
    1. Process the uploaded Excel file into a DataFrame.
    2. Dynamically create a corresponding database table.
    3. Perform a bulk insert of the data for efficient storage.

    Args:
        file (UploadFile): The uploaded Excel file.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Success message with table name or an error message.
    """
    df, table_name, table_id = process_excel_file(file)

    if df is None:
        return {"error": "The uploaded file contains no valid data"}

    # Create table dynamically based on DataFrame columns
    create_table(df, table_name, db, table_id)

    # Insert data into the created table
    await bulk_insert_using_copy(df, table_name, db, table_id)

    return {"message": "Data uploaded successfully", "table_name": table_name}
