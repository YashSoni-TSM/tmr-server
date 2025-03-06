from src.models.meta_table_model import MetaTable
from sqlalchemy.orm import Session
from fastapi import HTTPException
import json

def get_table_by_id(id: int, db: Session):
    table = db.query(MetaTable).filter(MetaTable.id == id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Ensure `table.region` is returned as a valid JSON object
    table.region = json.loads(table.region)
    return table


def get_all_tables(db: Session):
    tables = db.query(MetaTable).all()
    if not tables:
        raise HTTPException(status_code=404, detail="No tables found")
    return tables