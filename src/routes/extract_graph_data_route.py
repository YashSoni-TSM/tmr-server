from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.controllers.extract_graph_data_controller import extract_graph_data,extract_section_graph_data,get_regions
from src.schemas.extract_graph_data_schema import ExtractGraphDataSchema,GetRegionsSchema


router = APIRouter()

@router.post("/extract-graph-data")
async def extract_graph_data_router(req:ExtractGraphDataSchema, db:Session = Depends(get_db)):
    """
    Extracts data from the database for graph plotting.
    """
    if not req.table_id and not req.region:
        raise HTTPException(status_code=400, detail="Invalid request body.")

    return await extract_graph_data(req,db)


@router.post("/extract-section-graph-data")
async def extract_section_graph_data_router(req:ExtractGraphDataSchema, db:Session = Depends(get_db)):
    """
    Extracts data from the database for section graph plotting.
    """
    if not req.table_id and not req.region:
        raise HTTPException(status_code=400, detail="Invalid request body.")
    
    return await extract_section_graph_data(req,db)


@router.post("/get-regions")
async def get_regions_router(req:GetRegionsSchema,db:Session = Depends(get_db)):
    """
    Retrieves all regions from the database.
    """
    return await get_regions(req.table_id,db)

