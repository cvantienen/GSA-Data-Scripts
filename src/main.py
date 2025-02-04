import os
from src.test import get_db_connection
from src.test import generate_sample_contract_report, generate_sample_word

"""
Build using docker
    EXAMPLE -$ build -t container-name .
    
     docker build -t gsads .

Run the container:
    EXAMPLE -$  docker run -v /path/to/output:/app/output container-name
    
     docker run --rm -it -v $(pwd)/output:/app/output gsads

Full Command:
    docker build -t gsads . && docker run --rm -it -v $(pwd)/output:/app/output gsads
     
     """

def main():
    # Get the database connection
    conn = get_db_connection()
    
    try:
        # Generate different reports
        df = generate_sample_contract_report(conn, "47QSEA20D003B")
        
        # Ensure the output directory exists
        output_dir = "/app/output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the DataFrame to a CSV file inside the container
        df.write_csv(f"{output_dir}/path.csv")

        generate_sample_word(df, "10G FEDERAL INC")

    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    main()