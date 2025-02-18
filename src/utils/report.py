import os
import polars as pl
from datetime import date
from docxtpl import DocxTemplate
import subprocess
from .dfc import DataFrameCleaner
from test.sampleCompany import get_sample_company

dfc = DataFrameCleaner()


# TODO: Add the DataFrameCleaner class to the SamplePriceComp class.
class SamplePriceComp:
    """
    A class to perform sample price comparison and generate reports.

    Attributes:
    -----------
    conn : object
        Database connection object.
    company : Company
        Company information object.
    output_path : str
        Path to save the output files.
    query_results_df : DataFrame
        DataFrame to store the query results.
    contractor_items_df : DataFrame
        DataFrame to store the contractor items.
    comparison_df : DataFrame
        DataFrame to store the comparison data.
    analysis_results : dict
        Dictionary to store the analysis results.
            Keys:
            - 'company_name': str, Name of the company.
            - 'current_date': date, Current date.
            - 'contract_number': str, Contract number.
            - 'sam_uie': str, SAM UEI or "N/A".
            - 'option_end_date': str, Option end date in "Month Day, Year" format or "N/A".
            - 'days_until_option_end': int, Days until option end date or "N/A".
            - 'ultimate_end_date': str, Ultimate end date in "Month Day, Year" format or "N/A".
            - 'days_until_ultimate_end': int, Days until ultimate end date or "N/A".
            - 'below_competitor': int, Number of items below competitor price.
            - 'above_competitor': int, Number of items above competitor price.
            - 'avg_percent_diff': float, Average percent difference.
            - 'max_percent_diff': float, Maximum percent difference.
            - 'min_percent_diff': float, Minimum percent difference.
            - 'avg_price_deviation': float, Average price deviation.
            - 'max_price_deviation': float, Maximum price deviation.
            - 'min_price_deviation': float, Minimum price deviation.
            - 'deviate_more_than_1': int, Number of items deviating more than 1.
            - 'deviate_more_than_10': int, Number of items deviating more than 10.
            - 'deviate_more_than_100': int, Number of items deviating more than 100.
            - 'manufacture_avg_diff': list, List of dictionaries with manufacturer average differences.
            - 'comparison_items': list, List of dictionaries with comparison items.

    Methods:
    --------
    run_sample_report():
        Runs the sample report generation process.
    get_contractor_info():
        Stores the company information in the analysis_results dictionary.
    check_expiration_dates():
        Checks and formats the expiration dates, and calculates days until those dates.
    get_sample_products(query_file='src/querys/price_comp_random_sample.txt'):
        Gets 100 random items from the specific contract and matching items from competitors.
    get_contractor_items():
        Selects the columns to include in the final report from the original contractor's items.
    calculate_comparison_df():
        Calculates the average price for competitor products and the standard deviation of prices.
    comparison_statements():
        Stores the analysis results in the analysis_results dictionary.
    calculate_manufacture_average_diff():
        Provides manufacturer pricing overview and classifies as 'More Expensive' or 'Cheaper'.
    generate_pdf():
        Generates a Word document report based on the analysis results using a template.
    docx_to_pdf(word_file_path):
        Converts a Word document to PDF.
    """

    def __init__(self, conn, contract_number):
        self.conn = conn
        self.company = get_sample_company(contract_number)
        if not self.company:
            raise ValueError(f"Company with contract number {contract_number} not found.")

        self.output_path = "/app/output/"

        # DataFrames to store the query results and comparison data
        self.query_results_df = None
        self.contractor_items_df = None
        self.comparison_df = None
        self.manufacture_avg_diff_df = None  # Manufacture Average Difference

        # Analysis results Dictionary
        self.analysis_results = {}

    def run_sample_report(self):
        self.get_contractor_info()
        self.get_sample_products()
        self.get_contractor_items()
        self.calculate_comparison_df()
        self.comparison_statements()
        self.calculate_manufacture_average_diff()
        self.get_analysis_results_dict()
        self.generate_pdf()

    def get_contractor_info(self):
        """Store the company information in the dictionary attribute."""
        self.analysis_results['company_name'] = self.company.vendor
        self.analysis_results['current_date'] = date.today()
        self.analysis_results['contract_number'] = self.company.contract_number
        self.analysis_results['sam_uie'] = self.company.sam_uei or "N/A"
        self.check_expiration_dates()

    def check_expiration_dates(self):
        """Check and format the expiration dates, and calculate days until they expire."""
        option_end_date = self.company.current_option_period_end_date
        ultimate_end_date = self.company.ultimate_contract_end_date

        if option_end_date:
            self.analysis_results['option_end_date'] = option_end_date.strftime("%B %d, %Y")
            self.analysis_results['days_until_option_end'] = (option_end_date - date.today()).days
        else:
            self.analysis_results['option_end_date'] = "N/A"
            self.analysis_results['days_until_option_end'] = "N/A"

        if ultimate_end_date:
            self.analysis_results['ultimate_end_date'] = ultimate_end_date.strftime("%B %d, %Y")
            self.analysis_results['days_until_ultimate_end'] = (ultimate_end_date - date.today()).days
        else:
            self.analysis_results['ultimate_end_date'] = "N/A"
            self.analysis_results['days_until_ultimate_end'] = "N/A"

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
        query = query.replace("{contract_number}", self.company.contract_number)

        # Cast the price column to float
        self.query_results_df = pl.read_database(query, self.conn).with_columns(
            pl.col("price").cast(pl.Float64)
        )
        # get the number of items in the query results
        self.analysis_results['product_count'] = self.query_results_df.shape[0] - 100

        return

    def get_contractor_items(self):
        # Select the columns to include in the final report from the original contractors items
        self.contractor_items_df = self.query_results_df.select([
            "contractor_name",
            "contract_number",
            "manufacturer_part_number",
            "manufacturer_name",
            "product_name",
            "price",
        ]).filter(pl.col("contract_number") == self.company.contract_number)
        return

    def calculate_comparison_df(self):
        """Calculate the average price for competitor products and the standard deviation of prices for each product.
            Return a DataFrame with the results.
        """
        # average price for competitor products found in the query results
        # (excluding the contractor's items from average calculation)
        comp_average_price = self.query_results_df.filter(pl.col("source") == "competitor").group_by(
            "manufacturer_part_number").agg(
            pl.col("price").mean().alias("average_price_on_gsa")
        )
        # standard deviation of prices for each manufacturer_part_number
        price_deviation = self.query_results_df.group_by("manufacturer_part_number").agg(
            pl.col("price").std().alias("price_deviation")
        )
        # Combine the average price and price deviation into a single DataFrame
        average_and_deviation = comp_average_price.join(price_deviation, on="manufacturer_part_number", how="left")
        contractor_items_with_comps = self.contractor_items_df.join(average_and_deviation,
                                                                    on="manufacturer_part_number", how="left")

        # Calculate the percent difference from the Contractors price vs the average price on GSA
        #TODO fomat the percent difference so its not decimal value.
        self.comparison_df = contractor_items_with_comps.with_columns(
            ((pl.col("price") - pl.col("average_price_on_gsa")) / pl.col("average_price_on_gsa")).alias(
                "percent_difference")
        )

    def comparison_statements(self):
        """Store the analysis results in the class attributes."""
        # Calculate general statements based on the Price % difference From GSA Average
        self.analysis_results['below_competitor'] = self.comparison_df.filter(pl.col("percent_difference") < 0).shape[0]
        self.analysis_results['above_competitor'] = self.comparison_df.filter(pl.col("percent_difference") > 0).shape[0]
        self.analysis_results[
            'avg_percent_diff'] = f"{self.comparison_df.select(pl.col('percent_difference').mean()).item() * 100:.2f}%"
        self.analysis_results[
            'max_percent_diff'] = f"{self.comparison_df.select(pl.col('percent_difference').max()).item() * 100:.2f}%"
        self.analysis_results[
            'min_percent_diff'] = f"{self.comparison_df.select(pl.col('percent_difference').min()).item() * 100:.2f}%"
        self.analysis_results[
            'avg_price_deviation'] = f"${self.comparison_df.select(pl.col('price_deviation').mean()).item():.2f}"
        self.analysis_results[
            'max_price_deviation'] = f"${self.comparison_df.select(pl.col('price_deviation').max()).item():.2f}"
        self.analysis_results[
            'min_price_deviation'] = f"${self.comparison_df.select(pl.col('price_deviation').min()).item():.2f}"
        self.analysis_results['deviate_more_than_1'] = self.comparison_df.filter(pl.col("price_deviation") > 1).shape[0]
        self.analysis_results['deviate_more_than_10'] = self.comparison_df.filter(pl.col("price_deviation") > 10).shape[
            0]
        self.analysis_results['deviate_more_than_100'] = \
        self.comparison_df.filter(pl.col("price_deviation") > 100).shape[0]

    def calculate_manufacture_average_diff(self):
        """ Provides Manufacture Pricing Overview -  Calculates the average percent difference for pricing based on
            manufacturer and classify as 'More Expensive' or 'Cheaper'.
        """
        # Group by manufacturer_name and calculate the average percent difference
        man_avg_percent_diff = self.comparison_df.group_by("manufacturer_name").agg(
            pl.col("percent_difference").mean().alias("average_percent_difference")
        )
        # Add Column to Classify average percent difference
        self.manufacture_avg_diff_df = man_avg_percent_diff.with_columns(
            pl.when(pl.col("average_percent_difference") > 0)
            .then(pl.lit("Higher Price Average vs Competitor"))
            .when(pl.col("average_percent_difference") == 0)
            .then(pl.lit("Same Price As Competitors"))
            .when(pl.col("average_percent_difference").is_null())
            .then(pl.lit("No Competitors on GSA"))
            .otherwise(pl.lit("Lower Price Average vs Competitor"))
            .alias("comparison_string")
        )

    def get_analysis_results_dict(self):
        self.comparison_df = dfc.format_percent_columns(self.comparison_df, ["percent_difference"])
        self.comparison_df = dfc.format_price_columns(self.comparison_df, ["price", "average_price_on_gsa", "price_deviation"])
        self.manufacture_avg_diff_df = dfc.format_percent_columns(self.manufacture_avg_diff_df, ["average_percent_difference"])
        context = {
            'company_name': self.analysis_results['company_name'],
            'current_date': self.analysis_results['current_date'],
            'contract_number': self.analysis_results['contract_number'],
            'sam_uie': self.analysis_results['sam_uie'],
            'option_end_date': self.analysis_results['option_end_date'],
            'days_until_option_end': self.analysis_results['days_until_option_end'],
            'ultimate_end_date': self.analysis_results['ultimate_end_date'],
            'days_until_ultimate_end': self.analysis_results['days_until_ultimate_end'],
            'product_count': self.analysis_results['product_count'],
            'below_competitor': self.analysis_results['below_competitor'],
            'above_competitor': self.analysis_results['above_competitor'],
            'avg_percent_diff': self.analysis_results['avg_percent_diff'],
            'max_percent_diff': self.analysis_results['max_percent_diff'],
            'min_percent_diff': self.analysis_results['min_percent_diff'],
            'avg_price_deviation': self.analysis_results['avg_price_deviation'],
            'max_price_deviation': self.analysis_results['max_price_deviation'],
            'min_price_deviation': self.analysis_results['min_price_deviation'],
            'deviate_more_than_1': self.analysis_results['deviate_more_than_1'],
            'deviate_more_than_10': self.analysis_results['deviate_more_than_10'],
            'deviate_more_than_100': self.analysis_results['deviate_more_than_100'],
            'manufacture_avg_diff': self.manufacture_avg_diff_df.to_dicts(),  # Convert DataFrame to list of dicts
            'comparison_items': self.comparison_df.to_dicts(),  # Convert DataFrame to list of dicts
        }
        self.analysis_results = context

    def generate_pdf(self):
        """Generate a Word document report based on the analysis results using a template.
            Return the path to the generated PDF file.
            TODO: Create Separate Class for Report Generation for all reports: will take context & template and save as pdf
        """
        # Load the Word template
        template_path = "src/templates/template_report.docx"  # Update with the actual path to your template
        doc = DocxTemplate(template_path)

        # Render the template with the context
        doc.render(self.analysis_results)

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
