from fastapi import HTTPException
from src.models.meta_table_model import MetaTable
from sqlalchemy import text
import json

async def get_regions(table_id:str,db):
    table = db.query(MetaTable).filter(MetaTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found.")
    
    regions = json.loads(table.region)
    return regions


async def extract_graph_data(req, db):
    """
    Extracts aggregated year-wise data from the database for graph plotting,
    grouped by segment and formatted as an array of objects.
    """

    table_id = req.table_id
    region = req.region
    
    # Fetch table details
    table = db.query(MetaTable).filter(MetaTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found.")

    table_name = table.table_name

    # Identify all year-based columns dynamically
    result = db.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
    years = [col for col in result.keys() if col.startswith("year_")]

    if not years:
        raise HTTPException(status_code=400, detail="No year-based columns found.")

    # Build SUM query dynamically for selected years
    sum_columns = ", ".join([f"ROUND(SUM({year}::NUMERIC), 3) AS {year}" for year in years])

    # Optimize query by fetching all required data in a single execution
    query = f"""
        SELECT segment, {sum_columns}
        FROM {table_name}
        WHERE region=:region
        GROUP BY segment
    """
    
    sum_result = db.execute(text(query), {"region": region}).fetchall()

    # Restructure the response to match the required format
    transformed_data = {}

    for row in sum_result:
        segment = row[0]

        for i, year in enumerate(years):
            year_key = year.split("_")[1]
            value = row[i + 1]

            if year_key not in transformed_data:
                transformed_data[year_key] = {"year": year_key}

            transformed_data[year_key][segment] = value

    # Convert to list format
    formatted_output = list(transformed_data.values())

    return formatted_output



# async def extract_graph_data(req, db):
#     """
#     Extracts aggregated year-wise data from the database for graph plotting,
#     grouped by segment and region.
#     """

#     table_id = req.table_id
#     region = req.region
    
#     # Fetch table details
#     table = db.query(MetaTable).filter(MetaTable.id == table_id).first()
#     if not table:
#         raise HTTPException(status_code=404, detail="Table not found.")

#     table_name = table.table_name

#     # Identify all year-based columns dynamically
#     result = db.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
#     years = [col for col in result.keys() if col.startswith("year_")]

#     if not years:
#         raise HTTPException(status_code=400, detail="No year-based columns found.")

#     # Build SUM query dynamically for selected years
#     sum_columns = ", ".join([f"ROUND(SUM({year}::NUMERIC), 3) AS {year}" for year in years])

#     # Optimize query by fetching all required data in a single execution
#     query = f"""
#         SELECT region, segment, {sum_columns}
#         FROM {table_name}
#         WHERE region=:region
#         GROUP BY region, segment
#     """
    
#     sum_result = db.execute(text(query), {"region": region}).fetchall()

#     # Restructure the response
#     graph_data = {}

#     for row in sum_result:
#         region, segment = row[:2]
#         year_values = [{"year": year.split("_")[1], "value": row[i + 2]} for i, year in enumerate(years)]

#         if region not in graph_data:
#             graph_data[region] = []

#         graph_data[region].append({"segment": segment, "data": year_values})

#     return {"table_name": table_name, "regions": graph_data}


async def extract_section_graph_data(req, db):
    """
    Extracts data from the database for section graph plotting.
    """
    pass





# async def extract_graph_data(table_id, db):
#     """
#     Extracts aggregated year-wise data from the database for graph plotting,
#     grouped by segment and region.
#     """
#     # Fetch table details
#     table = db.query(MetaTable).filter(MetaTable.id == table_id).first()
#     if not table:
#         raise HTTPException(status_code=404, detail="Table not found.")

#     table_name = table.table_name
#     regions = json.loads(table.region)  # Convert stored JSON string into a list

#     # Identify all year-based columns dynamically
#     result = db.execute(text(f"SELECT * FROM {table_name} LIMIT 1"))
#     years = [col for col in result.keys() if col.startswith("year_")]

#     if not years:
#         raise HTTPException(status_code=400, detail="No year-based columns found.")

#     # Build SUM query dynamically for selected years
#     sum_columns = ", ".join([f"ROUND(SUM({year}::NUMERIC), 3) AS {year}" for year in years])

#     # Optimize query by fetching all required data in a **single** execution
#     query = f"""
#         SELECT region, segment, {sum_columns}
#         FROM {table_name}
#         WHERE region IN :regions
#         GROUP BY region, segment
#     """
#     sum_result = db.execute(text(query), {"regions": tuple(regions)}).fetchall()

#     # Restructure the response
#     graph_data = {}

#     for row in sum_result:
#         region, segment = row[:2]
#         year_values = [{"year": year.split("_")[1], "value": row[i + 2]} for i, year in enumerate(years)]

#         if region not in graph_data:
#             graph_data[region] = []

#         graph_data[region].append({"segment": segment, "data": year_values})

#     return {"table_name": table_name, "regions": graph_data}
