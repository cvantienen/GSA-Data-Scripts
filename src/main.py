from utils.config import get_db_connection
from utils.report import  SamplePriceComp
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
        contract_num = "47QSEA20D003B"
        # Generate different reports
        price_comp = SamplePriceComp(conn,  contract_num)
        price_comp.run_sample_report()
        print(price_comp.comparison_df)
        
    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    main()