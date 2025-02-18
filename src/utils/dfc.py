import polars as pl


class DataFrameCleaner:
    """A class of just static methods to clean the DataFrame columns and format the data."""

    def __init__(self):
        pass

    @staticmethod
    def format_percent_columns(df, column_list):
        # Format the percent_difference column to limit decimal places to 2
        for column in column_list:
            df = df.with_columns(
                pl.col(column).round(2)
            )
        for column in column_list:
            df = df.with_columns(
                pl.col(column).map_elements(
                    lambda x: f"{x:.2f}%" if x is not None else "N/A",
                    return_dtype=pl.Utf8
                )
            )
        return df

    @staticmethod
    def format_price_columns(df, column_list):
        # Format the percent_difference column to limit decimal places to 2
        for column in column_list:
            df = df.with_columns(
                pl.col(column).round(2)
            )
        for column in column_list:
            df = df.with_columns(
                pl.col(column).round(2).map_elements(
                    lambda x: f"${x:.2f}" if x is not None else "N/A",
                    return_dtype=pl.Utf8
                )
            )
        return df
