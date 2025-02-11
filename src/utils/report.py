import os
import polars as pl
from datetime import date
from docxtpl import DocxTemplate
import subprocess
from test.sampleCompany import get_sample_company

# TODO: Finish the SamplePriceComp class Refactor. Need to add the 100 sample items used
class SamplePriceComp:
    def __init__(self, conn, contract_number, output_path):
        self.conn = conn
        self.company = get_sample_company(contract_number)
        self.output_path = "/app/output/"
        self.query_results_df = None
        self.reference_items_df = None
        self.comparison_df = None

        # Analysis results
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
        self.manufacture_avg_diff = None


    def get_sample_products(self, query_file='src/querys/price_comp_random_sample.txt'):
        """Get 100 random items from the specific contract, along with all
          the matching items from competitors found from the database
           and return a DataFrame with the results.
        """
        # Load the SQL query from a file
        sql_query = query_file
        with open(sql_query, 'r') as file:
            query = file.read()

        # Replace the placeholder with the actual contract number & Query DB
        query = query.format(contract_number=self.company.contract_number)

        # Cast the price column to float
        self.query_results_df = pl.read_database(query, self.conn).with_columns(
            pl.col("price").cast(pl.Float64)
        )

        # Select the columns to include in the final report from the original contractors items
        self.reference_items_df = self.query_results_df.select([
            "contractor_name",
            "contract_number",
            "manufacturer_part_number",
            "manufacturer_name",
            "product_name",
            "price",
        ]).filter(pl.col("contract_number") == self.company.contract_number)
        return

    def calculate_comparison(self):
        """Calculate the average price for competitor products and the standard deviation of prices for each product.
            Return a DataFrame with the results.
        """
        # Get average for competitor products only
        comp_average_price = self.query_results_df.filter(pl.col("source") == "competitor").group_by("manufacturer_part_number").agg(
            pl.col("price").mean().alias("average_price_on_gsa")
        )
        # Calculate the standard deviation of prices for each manufacturer_part_number
        price_deviation = self.query_results_df.group_by("manufacturer_part_number").agg(
            pl.col("price").std().alias("price_deviation")
        )

        # Combine the average price and price deviation into a single DataFrame
        average_and_deviation = comp_average_price.join(price_deviation, on="manufacturer_part_number", how="left")

        # Combine the price comparison DataFrame with the reference items DataFrame
        reference_items_with_comps = self.reference_items_df.join(average_and_deviation, on="manufacturer_part_number", how="left")

        # Calculate the percent difference from the Contractors price vs the average price on GSA
        self.comparison_df = reference_items_with_comps.with_columns(
            ((pl.col("price") - pl.col("average_price_on_gsa")) / pl.col("average_price_on_gsa")).alias(
                "percent_difference")
        )
        return

    def store_analysis_statements(self):
        """Store the analysis results in the class attributes."""
        # Calculate general statements based on the Price % difference From GSA Average
        self.below_competitor = self.comparison_df.filter(pl.col("percent_difference") < 0).shape[0]
        self.above_competitor = self.comparison_df.filter(pl.col("percent_difference") > 0).shape[0]
        self.avg_percent_diff = self.comparison_df.select(pl.col("percent_difference").mean()).item()
        self.max_percent_diff = self.comparison_df.select(pl.col("percent_difference").max()).item()
        self.min_percent_diff = self.comparison_df.select(pl.col("percent_difference").min()).item()

        # Calculate Deviation
        self.avg_price_deviation = self.comparison_df.select(pl.col("price_deviation").mean()).item()
        self.max_price_deviation = self.comparison_df.select(pl.col("price_deviation").max()).item()
        self.min_price_deviation = self.comparison_df.select(pl.col("price_deviation").min()).item()

        # Count items that price deviation is more than $1, $10, and $100
        self.deviate_more_than_1 = self.comparison_df.filter(pl.col("price_deviation") > 1).shape[0]
        self.deviate_more_than_10 = self.comparison_df.filter(pl.col("price_deviation") > 10).shape[0]
        self.deviate_more_than_100 = self.comparison_df.filter(pl.col("price_deviation") > 100).shape[0]
        return

    def calculate_manufacture_average_diff(self, combined_df):
        """ Calculate the average percent difference for pricing based on
            manufacturer and classify as 'More Expensive' or 'Cheaper'.
        """

        # Group by manufacturer_name and calculate the average percent difference
        manufacturer_percent_diff = combined_df.group_by("manufacturer_name").agg(
            pl.col("percent_difference").mean().alias("average_percent_difference")
        )
        # Add Column to Classify average percent difference
        manufacturer_percent_diff = manufacturer_percent_diff.with_columns(
            pl.when(pl.col("average_percent_difference") >= 0)
                .then(pl.lit("More Expensive"))
                .otherwise(pl.lit("Cheaper"))
            .alias("comparison_string")
        )

        # Store the results in the class attribute, formatted as %
        self.manufacture_avg_diff = manufacturer_percent_diff.with_columns(
            pl.col("average_percent_difference").abs().map_elements(
                lambda x: f"{x * 100:.2f}%" if x is not None else "N/A",
                return_dtype=pl.Utf8
            )
        )


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
            'manufacture_analysis_df': self.manufacture_avg_diff.to_dicts()  # Convert DataFrame to list of dicts
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
        self.get_sample_products()
        self.analyze_data()
        self.generate_report()
