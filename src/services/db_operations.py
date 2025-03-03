import io
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from src.models.meta_table_model import MetaTable
from src.utils.utils import split_date

# ─────────────────────────────────────────────────────────────────
# TABLE CREATION
# ─────────────────────────────────────────────────────────────────

def create_table(df, table_name: str, db: Session, table_id: str):
    """
    Creates a table dynamically based on the given DataFrame columns.

    Args:
        df (DataFrame): Pandas DataFrame containing column names.
        table_name (str): Name of the new table.
        db (Session): SQLAlchemy database session.
        table_id (str): Unique ID for tracking the table in MetaTable.
    """
    column_definitions = ", ".join([f'"{col}" TEXT' for col in df.columns])
    
    create_table_query = f"""
        CREATE TABLE "{table_name}" (
            id SERIAL PRIMARY KEY,
            {column_definitions}
        )
    """
    
    try:
        db.execute(text(create_table_query))
        db.commit()

        # Register table in MetaTable
        meta_entry = MetaTable(id=table_id, table_name=table_name)
        db.add(meta_entry)
        db.commit()
        db.refresh(meta_entry)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating table: {str(e)}")

# ─────────────────────────────────────────────────────────────────
# BULK INSERT USING COPY COMMAND
# ─────────────────────────────────────────────────────────────────

async def bulk_insert_using_copy(df, table_name: str, db: Session, table_id: str):
    """
    Efficiently inserts large DataFrame data into the database using COPY.

    Args:
        df (DataFrame): Pandas DataFrame containing data.
        table_name (str): Target table name.
        db (Session): SQLAlchemy database session.
        table_id (str): Unique ID of the table in MetaTable.
    """
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, sep=',')
    buffer.seek(0)

    try:
        connection = db.connection()
        column_names = ", ".join([f'"{col}"' for col in df.columns])

        with connection.connection.cursor() as cursor:
            copy_sql = f'COPY "{table_name}" ({column_names}) FROM STDIN WITH CSV'
            cursor.copy_expert(copy_sql, buffer)
            connection.connection.commit()

        return await save_meta_data(table_id, db)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error in bulk insert: {str(e)}")

# ─────────────────────────────────────────────────────────────────
# DATA EXTRACTION UTILITIES
# ─────────────────────────────────────────────────────────────────

def extract_unique_values(db: Session, table_name: str, column: str):
    """
    Fetch distinct values from a specific column.

    Args:
        db (Session): SQLAlchemy database session.
        table_name (str): Table name.
        column (str): Column name.

    Returns:
        List of unique values.
    """
    query = text(f"SELECT DISTINCT {column} FROM {table_name} WHERE {column} IS NOT NULL")
    
    return [row[0] for row in db.execute(query).fetchall()]

def extract_columns_like(db: Session, table_name: str, keyword: str):
    """
    Retrieves column names matching a keyword.

    Args:
        db (Session): SQLAlchemy database session.
        table_name (str): Table name.
        keyword (str): Keyword for filtering columns.

    Returns:
        List of matching column names.
    """
    query = text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = :table_name 
        AND column_name LIKE :keyword 
        ORDER BY ordinal_position
    """)

    return [row[0] for row in db.execute(query, {"table_name": table_name, "keyword": f"%{keyword}%"}).fetchall()]

# ─────────────────────────────────────────────────────────────────
# SEGMENT & SUBSEGMENT HIERARCHY CREATION
# ─────────────────────────────────────────────────────────────────

def create_nested_segment(columns: list, table_name: str, db: Session):
    """
    Creates a hierarchical JSON structure based on column dependencies.

    Args:
        columns (list): List of hierarchical column names.
        table_name (str): Database table name.
        db (Session): SQLAlchemy database session.

    Returns:
        Nested dictionary representing the segment structure.
    """

    def fetch_values(filters: dict, level: int):
        """Recursively fetch unique values for each column."""
        if level >= len(columns):  
            return None

        column = columns[level]
        query = f"SELECT DISTINCT {column} FROM {table_name}"

        if filters:
            conditions = " AND ".join([f"{col} = :{col}" for col in filters.keys()])
            query += f" WHERE {conditions}"

        values = [row[0] for row in db.execute(text(query), filters).fetchall() if row[0] is not None]

        return {value: fetch_values({**filters, column: value}, level + 1) or {} for value in values}

    return fetch_values({}, 0)

# ─────────────────────────────────────────────────────────────────
# SAVE META DATA
# ─────────────────────────────────────────────────────────────────

async def save_meta_data(table_id: str, db: Session):
    """
    Updates and stores metadata for a given table.

    Args:
        table_id (str): Unique table ID.
        db (Session): SQLAlchemy database session.

    Returns:
        JSON-encoded updated metadata.
    """
    table = db.query(MetaTable).filter(MetaTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    table_name = table.table_name

    try:
        # Extract necessary metadata
        table.region = extract_unique_values(db, table_name, "region")
        segment_columns = extract_columns_like(db, table_name, "segment")
        table.segment_subsegment = create_nested_segment(segment_columns, table_name, db)

        date_columns = extract_columns_like(db, table_name, "year")
        if date_columns:
            table.start_year, table.end_year = map(split_date, [date_columns[0], date_columns[-1]])

        db.commit()
        db.refresh(table)

        return jsonable_encoder(table)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving metadata: {str(e)}")
