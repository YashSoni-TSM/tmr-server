import pandas as pd
import re
import uuid

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

    Args:
        name (str): Original column name.

    Returns:
        str: Sanitized column name.
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

    Args:
        name (str): Original table name.

    Returns:
        str: Sanitized table name.
    """
    return re.sub(r'\W+', '_', str(name).strip()).lower()

# ─────────────────────────────────────────────────────────────────
# METADATA EXTRACTION FROM 'HOME' SHEET
# ─────────────────────────────────────────────────────────────────

def extract_table_name(file) -> str:
    """
    Extracts 'Region' and 'Market Name' from the 'Home' sheet 
    to generate a unique table name.

    Assumptions:
    - Column A contains keys (e.g., "Region", "Market Name").
    - Column B contains values (e.g., "Asia-Pacific", "Graphite Market").

    Args:
        file: Uploaded Excel file.

    Returns:
        str: Generated unique table name.
    """
    # Load key-value metadata from the 'Home' sheet
    df = pd.read_excel(file.file, sheet_name="Home", usecols=[0, 1])

    # Drop empty rows and trim whitespace from key names
    df.dropna(inplace=True)
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip()

    # Convert to dictionary (lowercase keys for consistency)
    metadata_dict = {key.lower(): value for key, value in zip(df.iloc[:, 0], df.iloc[:, 1])}

    # Extract values
    region = sanitize_table_name(metadata_dict.get("region", ""))
    market_name = sanitize_table_name(metadata_dict.get("market name", ""))

    # Generate a short UUID for uniqueness
    unique_id = uuid.uuid4().hex[:8]

    # Construct the final table name
    table_name = f"{region}_{market_name}_{unique_id}"
    
    print(f"Generated Table Name: {table_name}")
    return table_name, unique_id

# ─────────────────────────────────────────────────────────────────
# EXCEL FILE PROCESSING FROM 'MASTER SHEET'
# ─────────────────────────────────────────────────────────────────

def process_excel_file(file) -> pd.DataFrame:
    """
    Reads an Excel file and cleans its data.

    - Reads from the "Master Sheet" (skipping first 5 rows).
    - Drops completely empty columns.
    - Sanitizes column names for SQL compatibility.

    Args:
        file: Uploaded Excel file.

    Returns:
        pd.DataFrame | None: Cleaned DataFrame or None if empty.
    """
    # Load data from the "Master Sheet"
    df = pd.read_excel(file.file, sheet_name="Master Sheet", skiprows=5)

    # Extract and print the unique table name
    table_name,table_id = extract_table_name(file)

    # Drop fully empty columns
    df.dropna(axis=1, how='all', inplace=True)

    # Return None if DataFrame is empty after cleaning
    if df.empty:
        return None

    # Apply column name sanitization
    df.columns = [sanitize_column_name(col) for col in df.columns]

    return df,table_name,table_id
