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

    # Calculate the comp average price for each manufacturer_part_number
    # for competitor products only
    comp_average_price = df.filter(pl.col("source") == "competitor").group_by("manufacturer_part_number").agg(
        pl.col("price").mean().alias("average_price_on_gsa")
    )

        # Extract the reference price for each manufacturer_part_number
    reference_price = df.filter(pl.col("source") == "reference").select(
        "manufacturer_part_number", "price"
    ).rename({"price": "reference_price"})


    # Calculate the standard deviation of prices for each manufacturer_part_number
    price_deviation = df.group_by("manufacturer_part_number").agg(
        pl.col("price").std().alias("price_deviation")
    )

     # Combine the competitor average price, reference price, and price deviation into a single DataFrame
    price_comparison = comp_average_price.join(reference_price, on="manufacturer_part_number", how="left")

    print("PRICE_COMPS_2")
    print("******************************************")
    print(price_comparison)

    price_comparison = price_comparison.join(price_deviation, on="manufacturer_part_number", how="left")

        # Select the columns you need
    selected_columns = df.select([
        "manufacturer_part_number",
        "manufacturer_name",
        "gsin",
        "date_last_updated",
    ]).unique()

    # Combine the selected columns with the calculated columns
    combined_df = selected_columns.join(price_comparison, on="manufacturer_part_number", how="left")


    print("PRICE_COMPS_3")
    print("******************************************")
    print(price_comparison)

    print("Selected columns")
    print("******************************************")
    print(selected_columns)


    
    print("Finished DF")
    print("******************************************")
    print(combined_df)




    return df