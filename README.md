# Polars Project

This project demonstrates how to use Polars to query a PostgreSQL database, analyze the data, and generate a PDF report. It is designed for quick analysis of small samples of data.

## Project Structure

```

├── src
│   ├── main.py          # Entry point of the application
│   └── utils
│       └── report.py    # Module for generating PDF reports
├── .env                 # Environment variables, including database URL
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd polars-project
   ```

2. **Create a virtual environment (optional but recommended):**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Configure the environment variables:**
   Create a `.env` file in the root directory and add your PostgreSQL database URL:
   ```
   DATABASE_URL=your_postgres_database_url
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

This will connect to the PostgreSQL database, perform the data analysis using Polars, and generate a PDF report.

## Dependencies

This project requires the following Python packages:
- Polars
- psycopg2 (PostgreSQL driver)
- ReportLab (for PDF generation)

## License

This project is licensed under the MIT License. See the LICENSE file for more details.