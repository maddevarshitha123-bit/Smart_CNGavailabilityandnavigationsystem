"""Central settings. Secrets are read from the .env file, never hard-coded."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")          # reads key=value lines from .env

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "smart_cng")
MAP_API_KEY = os.getenv("MAP_API_KEY", "")        # optional
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # optional

DATA_PATH = BASE_DIR / "data" / "cng_history.csv"
MODEL_PATH = BASE_DIR / "ml" / "model.pkl"
METRICS_PATH = BASE_DIR / "ml" / "metrics.json"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
SAMPLE_DATA_PATH = BASE_DIR / "database" / "sample_data.sql"

# Default map centre used when the user gives no location (Hyderabad, sample city)
DEFAULT_LOCATION = (17.4126, 78.5286)
DEFAULT_LOCATION_NAME = "Osmania University, Hyderabad (default)"

# Average city speed (km/h) used to estimate travel time when routing API is unavailable
AVG_SPEED_KMH = 25
