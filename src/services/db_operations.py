import io
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.models.meta_table_model import MetaTable

def create_table(df, table_name, db: Session):
    """Create a table dynamically based on DataFrame columns."""
    column_definitions = ", ".join([f'"{col}" TEXT' for col in df.columns])
    create_table_query = f'CREATE TABLE "{table_name}" (id SERIAL PRIMARY KEY, {column_definitions})'
    
    db.execute(text(create_table_query))
    db.commit()

    meta_entry = MetaTable(table_name=table_name)
    db.add(meta_entry)
    db.commit()

def bulk_insert_using_copy(df, table_name, db: Session):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, sep=',')
    buffer.seek(0)

    connection = db.connection()

    column_names = ", ".join([f'"{col}"' for col in df.columns])

    with connection.connection.cursor() as cursor:
        copy_sql = f'COPY "{table_name}" ({column_names}) FROM STDIN WITH CSV'
        cursor.copy_expert(copy_sql, buffer)
        connection.connection.commit()
