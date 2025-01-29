from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables from .env file
load_dotenv()

# Get the PostgreSQL database connection details from the environment variables
DB_NAME = os.getenv("GSADB_NAME")
DB_USER = os.getenv("GSADB_USER")
DB_PASSWORD = os.getenv("GSADB_PASSWORD")
DB_HOST = os.getenv("GSADB_HOST")
DB_PORT = os.getenv("GSADB_PORT")

def get_db_connection():
    """Establish and return a connection to the PostgreSQL database."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
