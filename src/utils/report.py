import polars as pl


def generate_sample_contract_report(conn):
    """Generate a sample report for 100 products that a contract has and returns up to 3
      competitor products for each."""
    query = """
    WITH reference_items AS (
        -- Get 100 random items from the specific contract
        SELECT *
        FROM gsa_product_extract_jan2024
        WHERE contract_number = 'GS-07F-0577T'
        ORDER BY RANDOM()  -- Randomize the selection of the 100 items
        LIMIT 100
    ),
    competitor_items AS (
        -- Get all items with the same manufacturer_part_number from different contracts
        SELECT *
        FROM gsa_product_extract_jan2024 gi
        WHERE gi.contract_number != 'GS-07F-0577T'  -- Ensure items are from different contracts
        AND gi.manufacturer_part_number IN (SELECT manufacturer_part_number FROM reference_items)
    )
    -- Get 3 matches for each item from the contract, with columns varying depending on number of matches found
    SELECT ref.*,
           comp1.*,
           comp2.*,
           comp3.*
    FROM reference_items ref
    LEFT JOIN (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY manufacturer_part_number ORDER BY RANDOM()) as rn
        FROM competitor_items
    ) comp1 ON ref.manufacturer_part_number = comp1.manufacturer_part_number AND comp1.rn = 1
    LEFT JOIN (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY manufacturer_part_number ORDER BY RANDOM()) as rn
        FROM competitor_items
    ) comp2 ON ref.manufacturer_part_number = comp2.manufacturer_part_number AND comp2.rn = 2
    LEFT JOIN (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY manufacturer_part_number ORDER BY RANDOM()) as rn
        FROM competitor_items
    ) comp3 ON ref.manufacturer_part_number = comp3.manufacturer_part_number AND comp3.rn = 3
    ORDER BY ref.jprod_id;
    """
    df = pl.read_sql(query, conn)

    print(df)
    # Perform data analysis (example: calculate mean price of products)
    