from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.controllers.meta_table_controller import get_table_by_id, get_all_tables

router = APIRouter()

@router.get("/tables/{id}")
async def get_table_by_id_router(id: str, db: Session = Depends(get_db)):
    if not id:
        raise HTTPException(status_code=400, detail="Table ID is required.")
    return get_table_by_id(id,db)

@router.get("/tables")
async def get_all_tables_router(db: Session = Depends(get_db)):
    return get_all_tables(db)
