import pandas as pd
import re

def sanitize_column_name(name: str) -> str:
    """Ensure column names are SQL-friendly."""
    name = str(name).strip()
    name = re.sub(r'\W+', '_', name)  # Replace special characters with '_'

    if re.match(r'^\d', name):  # If column starts with a number, prefix with 'year_'
        name = f"year_{name}"

    return name.lower()

def process_excel_file(file) -> pd.DataFrame:
    """Read and clean the Excel file."""
    df = pd.read_excel(file.file, skiprows=5, sheet_name="Master Sheet")

    # Drop fully empty rows and columns
    df.dropna(axis=1,inplace=True)

    if df.empty:
        return None

    # Sanitize column names
    df.columns = [sanitize_column_name(col) for col in df.columns]

    return df
