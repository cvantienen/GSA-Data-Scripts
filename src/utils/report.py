import polars as pl
from docx import Document
from src.test.sampleCompany import get_sample_company


def generate_sample_contract_report(conn, contract_number):
    """Generate a sample report for 100 products that a contract has and returns up to 3
      competitor products for each.

        Args:
            conn (Connection): The database connection.
            contract_number (str): The contract number to generate the report for.

        Returns:
            combined_df (pl.DataFrame): The DataFrame with the combined data.

      """
    query = f"""
    WITH reference_items AS (
        -- Get 100 random items from the specific contract
        SELECT *
        FROM gsa_product_extract_jan2024
        WHERE contract_number =  '{contract_number}'
        ORDER BY RANDOM()  -- Randomize the selection of the 100 items
        LIMIT 100
    ),
    competitor_items AS (
        -- Get all items with the same manufacturer_part_number from different contracts
        SELECT *
        FROM gsa_product_extract_jan2024 gi
        WHERE gi.contract_number != '{contract_number}'  -- Ensure items are from different contracts
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




class SamplePriceComp:
    def __init__(self, conn, contract_number):
        self.conn = conn
        self.company =  get_sample_company(contract_number)
        self.df = None
        self.analysis_results = None

    def get_100_random_products(self):
        """ Get 100 random items from the specific contract from the database and load it into a DataFrame."""
        query = f"""
        WITH reference_items AS (
            SELECT *
            FROM gsa_product_extract_jan2024
            WHERE contract_number =  '{self.contract_number}'
            ORDER BY RANDOM()  -- Randomize the selection of the 100 items
            LIMIT 100
        ),
        competitor_items AS (
            -- Get all items with the same manufacturer_part_number from different contracts
            SELECT *
            FROM gsa_product_extract_jan2024 gi
            WHERE gi.contract_number != '{self.contract_number}'  -- Ensure items are from different contracts
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
        self.df = pl.read_database(query, self.conn)
        self.df = self.df.with_columns(pl.col("price").cast(pl.Float64))

    def analyze_data(self):
        """Analyze the DataFrame and store the results."""
        df = self.df

        # Calculate general statements based on the Price % difference From GSA Average
        below_competitor = df.filter(pl.col("percent_difference") < 0).shape[0]
        above_competitor = df.filter(pl.col("percent_difference") > 0).shape[0]
        avg_percent_diff = df.select(pl.col("percent_difference").mean()).item()
        max_percent_diff = df.select(pl.col("percent_difference").max()).item()
        min_percent_diff = df.select(pl.col("percent_difference").min()).item()

        # Calculate Deviation
        avg_price_deviation = df.select(pl.col("price_deviation").mean()).item()
        max_price_deviation = df.select(pl.col("price_deviation").max()).item()
        min_price_deviation = df.select(pl.col("price_deviation").min()).item()

        # Count items that price deviation is more than $1, $10, and $100
        count_more_than_1 = df.filter(pl.col("price_deviation") > 1).shape[0]
        count_more_than_10 = df.filter(pl.col("price_deviation") > 10).shape[0]
        count_more_than_100 = df.filter(pl.col("price_deviation") > 100).shape[0]

        manufacturers = df.select("manufacturer_name").unique()

        self.analysis_results = {
            "below_competitor": below_competitor,
            "above_competitor": above_competitor,
            "avg_percent_diff": avg_percent_diff,
            "max_percent_diff": max_percent_diff,
            "min_percent_diff": min_percent_diff,
            "avg_price_deviation": avg_price_deviation,
            "max_price_deviation": max_price_deviation,
            "min_price_deviation": min_price_deviation,
            "count_more_than_1": count_more_than_1,
            "count_more_than_10": count_more_than_10,
            "count_more_than_100": count_more_than_100,
            "manufacturers": manufacturers
        }

    def generate_report(self):
        """Generate a Word document report based on the analysis results."""
        # Create a Word document
        doc = Document()
        doc.add_heading(f'Sample GSA Contract Analysis', 0)
        doc.add_heading(f'GSA Contractor: {self.company}')
        doc.add_heading(f'Contract Number: {self.company.contract_number}', level=1)
        doc.add_heading(f'Manufacturer: {self.company.url}', level=1)
        doc.add_heading(f'Manufacturer: {self.company.url}', level=1)




        results = self.analysis_results
        doc.add_paragraph(f"- Number of items below competitor price: {results['below_competitor']}")
        doc.add_paragraph(f"- Number of items above competitor price: {results['above_competitor']}")
        doc.add_paragraph(f"- Average percent difference: {results['avg_percent_diff']:.2f}%")
        doc.add_paragraph(f"- Max percent difference: {results['max_percent_diff']:.2f}%")
        doc.add_paragraph(f"- Min percent difference: {results['min_percent_diff']:.2f}%")
        doc.add_paragraph(f"- Average price deviation: ${results['avg_price_deviation']:.2f}")
        doc.add_paragraph(f"- Max price deviation: ${results['max_price_deviation']:.2f}")
        doc.add_paragraph(f"- Min price deviation: ${results['min_price_deviation']:.2f}")
        doc.add_paragraph(f"- Count of items with price deviation more than $1: {results['count_more_than_1']}")
        doc.add_paragraph(f"- Count of items with price deviation more than $10: {results['count_more_than_10']}")
        doc.add_paragraph(f"- Count of items with price deviation more than $100: {results['count_more_than_100']}")

        doc.save(output_path)

"""
# Example usage
if __name__ == "__main__":
    conn = get_db_connection()
    contract_number = '47QSEA20D003B'
    report = SamplePriceComp(conn, contract_number)
    report.fetch_data()
    report.analyze_data()
    report.generate_report()
    conn.close()

"""