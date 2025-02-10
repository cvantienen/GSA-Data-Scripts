import os
import polars as pl
from datetime import date
from docxtpl import DocxTemplate
import subprocess
from test.sampleCompany import get_sample_company

# TODO: Add more analysis methods, and styling to the report
class SamplePriceComp:
    def __init__(self, conn, contract_number):
        self.conn = conn
        self.company = get_sample_company(contract_number)
        self.df = None
        self.manufacture_analysis_df = None
        self.analysis_results = None
        self.output_path = "/app/output/"
        
        # Analysis results as attributes
        self.product_count = None
        self.below_competitor = None
        self.above_competitor = None
        self.avg_percent_diff = None
        self.max_percent_diff = None
        self.min_percent_diff = None
        self.avg_price_deviation = None
        self.max_price_deviation = None
        self.min_price_deviation = None
        self.deviate_more_than_1 = None
        self.deviate_more_than_10 = None
        self.deviate_more_than_100 = None


    def get_100_random_products(self):
        """ Get 100 random items from the specific contract
            from the database and load it into a DataFrame."""
        query = f"""
        WITH reference_items AS (
            SELECT *
            FROM gsa_product_extract_jan2024
            WHERE contract_number =  '{self.company.contract_number}'
            ORDER BY RANDOM()  -- Randomize the selection of the 100 items
            LIMIT 100
        ),
        competitor_items AS (
            -- Get all items with the same manufacturer_part_number from different contracts
            SELECT *
            FROM gsa_product_extract_jan2024 gi
            WHERE gi.contract_number != '{self.company.contract_number}'  -- Ensure items are from different contracts
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

        print(f"Loaded {self.product_count} products for analysis.")

    def analyze_data(self):
        """Analyze the Sample DataFrame and store the results."""
        df = self.df

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

        # Select the columns to include in the final report from the original contractors items
        selected_columns = df.select([
            "contractor_name",
            "contract_number",
            "manufacturer_part_number",
            "manufacturer_name",
            "product_name",
            "price",
        ]).filter(pl.col("contract_number") == self.company.contract_number)

        # Combine the selected columns with the calculated columns
        combined_df = selected_columns.join(price_comparison, on="manufacturer_part_number", how="left")

        # Calculate the percent difference from the Contractors price vs the average price on GSA
        combined_df = combined_df.with_columns(
            ((pl.col("price") - pl.col("average_price_on_gsa")) / pl.col("average_price_on_gsa")).alias("percent_difference")
        )

        # Calculate general statements based on the Price % difference From GSA Average
        self.below_competitor = combined_df.filter(pl.col("percent_difference") < 0).shape[0]
        self.above_competitor = combined_df.filter(pl.col("percent_difference") > 0).shape[0]
        self.avg_percent_diff = combined_df.select(pl.col("percent_difference").mean()).item()
        self.max_percent_diff = combined_df.select(pl.col("percent_difference").max()).item()
        self.min_percent_diff = combined_df.select(pl.col("percent_difference").min()).item()

        # Calculate Deviation
        self.avg_price_deviation = combined_df.select(pl.col("price_deviation").mean()).item()
        self.max_price_deviation = combined_df.select(pl.col("price_deviation").max()).item()
        self.min_price_deviation = combined_df.select(pl.col("price_deviation").min()).item()

        # Count items that price deviation is more than $1, $10, and $100
        self.deviate_more_than_1 = combined_df.filter(pl.col("price_deviation") > 1).shape[0]
        self.deviate_more_than_10 = combined_df.filter(pl.col("price_deviation") > 10).shape[0]
        self.deviate_more_than_100 = combined_df.filter(pl.col("price_deviation") > 100).shape[0]

        # Group by manufacturer_name and calculate the average percent difference
        manufacturer_percent_diff = combined_df.group_by("manufacturer_name").agg(
            pl.col("percent_difference").mean().alias("average_percent_difference")
        )

        manufacturer_percent_diff = manufacturer_percent_diff.with_columns(
            pl.when(pl.col("average_percent_difference") >= 0)
                .then(pl.lit("More Expensive"))
                .otherwise(pl.lit("Cheaper"))
            .alias("comparison_string")
        )

        formatted_percent_manufacture_diff = manufacturer_percent_diff.with_columns(
            pl.col("average_percent_difference").abs().map_elements(
                lambda x: f"{x * 100:.2f}%" if x is not None else "N/A",
                return_dtype=pl.Utf8
            )
        )

        self.manufacture_analysis_df = formatted_percent_manufacture_diff


    def generate_report(self):
        """Generate a Word document report based on the analysis results using a template."""
        # Load the Word template
        template_path = "src/templates/template_report.docx"  # Update with the actual path to your template
        doc = DocxTemplate(template_path)

        # Prepare the context with the data to fill in the template
        context = {
            'company_name': self.company,
            'current_date': date.today(),
            'contract_number': self.company.contract_number,
            'sam_uie': self.company.sam_uei,
            'option_end_date': self.company.current_option_period_end_date,
            'ultimate_end_date': self.company.ultimate_contract_end_date,
            'product_count': self.product_count,
            'below_competitor': self.below_competitor,
            'above_competitor': self.above_competitor,
            'avg_percent_diff': f"{self.avg_percent_diff:.2f}%",
            'max_percent_diff': f"{self.max_percent_diff:.2f}%",
            'min_percent_diff': f"{self.min_percent_diff:.2f}%",
            'avg_price_deviation': f"${self.avg_price_deviation:.2f}",
            'max_price_deviation': f"${self.max_price_deviation:.2f}",
            'min_price_deviation': f"${self.min_price_deviation:.2f}",
            'deviate_more_than_1': self.deviate_more_than_1,
            'deviate_more_than_10': self.deviate_more_than_10,
            'deviate_more_than_100': self.deviate_more_than_100,
            'manufacture_analysis_df': self.manufacture_analysis_df.to_dicts()  # Convert DataFrame to list of dicts
        }

        # Render the template with the context
        doc.render(context)

        # Save the rendered Word document
        file_name = f"GSA_Report_{self.company.contract_number}.docx"
        word_file_path = os.path.join(self.output_path, file_name)
        doc.save(word_file_path)

        # Convert the Word document to PDF
        pdf_file_path = self.docx_to_pdf(word_file_path)

        # remove the Word file
        os.remove(word_file_path)

        return pdf_file_path

    def docx_to_pdf(self, word_file_path):
        subprocess.call(['soffice',
                         '--headless',
                         '--convert-to',
                         'pdf',
                         '--outdir',
                         self.output_path,
                         word_file_path])

        # Get the base name of the input document (without extension)
        base_name = os.path.splitext(os.path.basename(word_file_path))[0]

        # Create the output PDF file path
        pdf_path = os.path.join(self.output_path, base_name + '.pdf')

        # Return the PDF file path
        return pdf_path

    def run_sample_report(self):
        self.get_100_random_products()
        self.analyze_data()
        self.generate_report()

"""    def docx_to_pdf(self, word_file_path):

        # Convert the Word document file path to the PDF file path
        pdf_file_name = f"GSA_Report_{self.company.contract_number}.pdf"
        pdf_file_path = os.path.join(self.output_path, pdf_file_name)

        return pdf_file_path
"""


"""
        # Add the table after rendering
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False
        table.columns[0].width = Inches(2)
        table.columns[1].width = Inches(2)

        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text = "Manufacturer Name"
        header_cells[1].text = "Average Percent Difference"

        # Add data rows
        for item in self.manufacture_analysis_df:
            row_cells = table.add_row().cells
            row_cells[0].text = item['manufacturer_name']
            row_cells[1].text = item['average_percent_difference']
"""
