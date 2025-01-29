from utils.config import get_db_connection 
from utils.report import generate_sample_contract_report


def main():
    # Get the database connection
    conn = get_db_connection()
    
    try:
        # Generate different reports
        generate_sample_contract_report(conn)
        # Add more report functions as needed
    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    main()