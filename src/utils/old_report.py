
def generate_sample_contract_report(conn, contract_number):
    """Generate a sample report for 100 products that a contract has and returns up to 3
      competitor products for each.

        Args:
            conn (Connection): The database connection.
            contract_number (str): The contract number to generate the report for.

        Returns:
            combined_df (pl.DataFrame): The DataFrame with the combined data.

      """

    df = pl.read_database(query, conn)

    # Make Correct Data Type so shit doesn't fuck up calculations
    df = df.with_columns(pl.col("price").cast(pl.Float64))

    # Calculate the comp average price for each manufacturer_part_number
    # for competitor products only
    comp_average_price = df.filter(pl.col("source") == "competitor").group_by("manufacturer_part_number").agg(
        pl.col("price").mean().alias("average_price_on_gsa")
    )

    # Calculate the standard deviation of prices for each manufacturer_part_number
    price_deviation = df.group_by("manufacturer_part_number").agg(
        pl.col("price").std().alias("price_deviation")
    )

    # Combine the average price and price deviation into a single DataFrame
    price_comparison = comp_average_price.join(price_deviation, on="manufacturer_part_number", how="left")

    print("PRICE_COMPS_1")
    print("******************************************")
    print(price_comparison)

    # Select the columns to include in the final report from the original contractors items
    selected_columns = df.select([
        "contractor_name",
        "contract_number",
        "manufacturer_part_number",
        "manufacturer_name",
        "product_name",
        "price",
    ]).filter(pl.col("contract_number") == contract_number)

    # Combine the selected columns with the calculated columns
    combined_df = selected_columns.join(price_comparison, on="manufacturer_part_number", how="left")

    # Calculate the percent difference from the Contractors price vs the average price on GSA
    combined_df = combined_df.with_columns(
        ((pl.col("price") - pl.col("average_price_on_gsa")) / pl.col("average_price_on_gsa")).alias("percent_difference")
    )

    return combined_df


def generate_sample_word(df, company):
    """Create a Word report from the DataFrame and save it to the output directory.
        The report includes general statements about the data and a detailed table of the data.

        Args:
            df (pl.DataFrame): The DataFrame to include in the report.
            company (str): The directory to save the report to.

        Returns:
            doc (Document): The Word document object.
    """

    # Create a Word document
    doc = Document()
    doc.add_heading(f'Contract Report', 0)
    doc.add_heading(f'Contract Number: {company}', level=1)


    # Add % difference from average statements to the document
    doc.add_heading('General Statements:', level=1)
    doc.add_paragraph(f"- Number of items below competitor price: {below_competitor}")
    doc.add_paragraph(f"- Number of items above competitor price: {above_competitor}")
    doc.add_paragraph(f"- Average percent difference: {avg_percent_diff:.2%}")
    doc.add_paragraph(f"- Maximum percent difference: {max_percent_diff:.2%}")
    doc.add_paragraph(f"- Minimum percent difference: {min_percent_diff:.2%}")

    # Add price deviation statements to the document
    doc.add_paragraph(f"- Average price deviation: {avg_price_deviation:.2f}")
    doc.add_paragraph(f"- Maximum price deviation: {max_price_deviation:.2f}")
    doc.add_paragraph(f"- Minimum price deviation: {min_price_deviation:.2f}")

    # Add price deviation statements of more than $1, $10, and $100
    doc.add_paragraph(f"- Count of items with price_deviation more than $1: {count_more_than_1}")
    doc.add_paragraph(f"- Count of items with price_deviation more than $10: {count_more_than_10}")
    doc.add_paragraph(f"- Count of items with price_deviation more than $100: {count_more_than_100}")

    # Add details about the manufactures
    doc.add_heading('Manufactures Used In Sample:', level=1)
    for manufacturer in manufacturers:
        doc.add_paragraph(f"- {manufacturer}")

    # Add detailed table from DataFrame
    doc.add_heading('Detailed Analysis:', level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, column in enumerate(df.columns):
        hdr_cells[i].text = column

    for row in df.to_dicts():
        row_cells = table.add_row().cells
        for i, (key, value) in enumerate(row.items()):
            row_cells[i].text = str(value)

    # Output directory
    output_dir = "/app/output"

    # Save the document to a file
    doc.save(f"{output_dir}/report.docx")

    print(f"Report saved to {output_dir}/report.docx")
    return
