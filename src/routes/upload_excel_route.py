from fastapi import UploadFile, File, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.services.excel_processor import process_and_store_excel,process_zip_file
import magic


router = APIRouter()

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Handles both direct Excel file uploads and ZIP file uploads containing Excel files.
    """
    file_ext = file.filename.lower().split(".")[-1]

    # Read file contents for validation
    contents = await file.read()

    # Validate MIME type
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(contents)

    if file_ext in ["xls", "xlsx"]:
        # Process a single Excel file
        return await process_and_store_excel(file, contents, db)

    elif file_ext == "zip" and file_type == "application/zip":
        return await process_zip_file(contents, db)

    else:
        raise HTTPException(status_code=400, detail="Only ZIP or Excel files are allowed")