import polars as pl


def generate_sample_contract_report(conn):
    """Generate a sample report for 100 products that a contract has and returns up to 3
      competitor products for each."""
    query = """
    WITH reference_items AS (
        -- Get 100 random items from the specific contract
        SELECT *
        FROM gsa_product_extract_jan2024
        WHERE contract_number = '47QSEA20D003B'
        ORDER BY RANDOM()  -- Randomize the selection of the 100 items
        LIMIT 100
    ),
    competitor_items AS (
        -- Get all items with the same manufacturer_part_number from different contracts
        SELECT *
        FROM gsa_product_extract_jan2024 gi
        WHERE gi.contract_number != '47QSEA20D003B'  -- Ensure items are from different contracts
        AND gi.manufacturer_part_number IN (SELECT manufacturer_part_number FROM reference_items)
    )
    -- Combine reference items with their matches
    SELECT ref.*, 'reference' AS source
    FROM reference_items ref
    UNION ALL
    SELECT comp.*, 'competitor' AS source
    FROM competitor_items comp
    ORDER BY jprod_id;
    """
    df = pl.read_database(query, conn)

    # Ensure the price column is correctly populated and is of numeric type
    df = df.with_columns(pl.col("price").cast(pl.Float64))


    # Check data types
    print(df.describe())
    print(df)

    # Group by manufacturer_part_number and source, then calculate average price
    # This gives the average price for each manufacturer_part_number from Competitor and Reference
    # the average price does not include the reference price, only the competitor price
    
    price_comparison = df.group_by(["manufacturer_part_number", "source"]).agg(
        pl.col("price").mean().alias("average_price")
    )
    # Show the result
    print(price_comparison)


    # Pivot the table to compare the prices side-by-side
    pivot_comparison = price_comparison.pivot(
        values="average_price", 
        columns="source", 
        aggregate_function="first"
    )

    # Show the result
    print(pivot_comparison)


    # Calculate the standard deviation of prices for each manufacturer_part_number
    price_deviation = df.group_by("manufacturer_part_number").agg(
        pl.col("price").std().alias("price_deviation")
    )

    
    print(price_deviation)


    return df