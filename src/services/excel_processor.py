import pandas as pd
import re
import uuid
import io
import zipfile
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from src.services.db_operations import create_table, bulk_insert_using_copy

# ─────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS FOR SANITIZATION
# ─────────────────────────────────────────────────────────────────

def sanitize_column_name(name: str) -> str:
    """
    Convert column names into a SQL-friendly format.

    - Strips leading/trailing spaces.
    - Replaces special characters with underscores (_).
    - Prefixes column names starting with a digit with "year_".
    - Converts everything to lowercase.
    """
    name = str(name).strip()
    name = re.sub(r'\W+', '_', name)  # Replace special characters with '_'
    return f"year_{name}" if re.match(r'^\d', name) else name.lower()


def sanitize_table_name(name: str) -> str:
    """
    Convert table names into a SQL-friendly format.

    - Strips leading/trailing spaces.
    - Replaces special characters with underscores (_).
    - Converts everything to lowercase.
    """
    return re.sub(r'\W+', '_', str(name).strip()).lower()

# ─────────────────────────────────────────────────────────────────
# METADATA EXTRACTION FROM 'HOME' SHEET
# ─────────────────────────────────────────────────────────────────

def extract_table_name(file) -> str:
    """
    Extracts 'Region' and 'Market Name' from the 'Home' sheet to generate a unique table name.
    """
    df = pd.read_excel(file.file, sheet_name="Home", usecols=[0, 1])
    df.dropna(inplace=True)  # Drop empty rows
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip()
    
    metadata_dict = {key.lower(): value for key, value in zip(df.iloc[:, 0], df.iloc[:, 1])}
    
    region = sanitize_table_name(metadata_dict.get("region", ""))
    market_name = sanitize_table_name(metadata_dict.get("market name", ""))
    
    unique_id = uuid.uuid4().hex[:8]  # Generate a short UUID for uniqueness
    table_name = f"{region}_{market_name}_{unique_id}"
    
    print(f"Generated Table Name: {table_name}")
    return table_name, unique_id

# ─────────────────────────────────────────────────────────────────
# EXCEL FILE PROCESSING FROM 'MASTER SHEET'
# ─────────────────────────────────────────────────────────────────

def process_excel_file(file) -> pd.DataFrame:
    """
    Reads an Excel file and cleans its data.
    """
    df = pd.read_excel(file.file, sheet_name="Master Sheet", skiprows=5)
    table_name, table_id = extract_table_name(file)
    
    df.dropna(axis=1, inplace=True)  # Drop fully empty columns
    if df.empty:
        return None
    
    df.columns = [sanitize_column_name(col) for col in df.columns]
    return df, table_name, table_id

# ─────────────────────────────────────────────────────────────────
# FILE UPLOAD HANDLING
# ─────────────────────────────────────────────────────────────────

async def process_and_store_excel(file: UploadFile, contents: bytes, db: Session):
    """
    Processes and stores an individual Excel file.
    """
    df, table_name, table_id = process_excel_file(UploadFile(filename=file.filename, file=io.BytesIO(contents)))
    
    if df is None:
        raise HTTPException(status_code=400, detail=f"The file {file.filename} contains no valid data")
    
    create_table(df, table_name, db, table_id)
    await bulk_insert_using_copy(df, table_name, db, table_id)
    
    return {"message": "Data uploaded successfully", "table_name": table_name}


async def process_zip_file(contents: bytes, db: Session):
    """
    Extracts and processes Excel files from a ZIP archive.
    """
    zip_buffer = io.BytesIO(contents)
    extracted_files = []
    excel_upload_responses = []
    failed_files = []
    
    try:
        with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith((".xls", ".xlsx")):
                    file_data = zip_ref.read(file_name)
                    extracted_files.append(UploadFile(filename=file_name, file=io.BytesIO(file_data)))
        
        if not extracted_files:
            raise HTTPException(status_code=400, detail="No valid Excel files found in ZIP")
        
        # Process extracted Excel files
        for extracted_file in extracted_files:
            try:
                response = await process_and_store_excel(extracted_file, extracted_file.file.read(), db)
                excel_upload_responses.append({"file": extracted_file.filename, "response": response})
            except Exception as e:
                failed_files.append({"file": extracted_file.filename, "error": str(e)})
    
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Corrupt or invalid ZIP file")
    
    return {
        "extracted_files": [f.filename for f in extracted_files],
        "excel_upload_results": excel_upload_responses,
        "failed_files": failed_files  # Return the list of failed files
    }