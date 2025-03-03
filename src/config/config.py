import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global config variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
# DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # Convert to boolean
