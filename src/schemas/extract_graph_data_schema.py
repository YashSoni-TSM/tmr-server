from pydantic import BaseModel

class ExtractGraphDataSchema(BaseModel):
    table_id: str
    region: str