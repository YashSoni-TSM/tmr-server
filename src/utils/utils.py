def split_date(date):
    """Extract year from column name (e.g., 'year_2025' → 2025)."""
    return int(date.split("_")[1])