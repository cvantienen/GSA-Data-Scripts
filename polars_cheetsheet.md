# Polars DataFrame Operations

## Reading Data

You used `pl.read_csv` to read the penguins dataset from a URL. The dataset contains missing values represented as `NA`.

## Checking Properties

- The `.shape` attribute helps you check the dimensions (rows, columns) of the DataFrame.
- The `.head()` method shows the first few rows of the DataFrame.
- The `.columns` attribute returns a list of column names.

## Filtering Rows

- You filtered rows using `.filter()` with conditions, including:
  - Checking for non-null values.
  - Applying logical conditions like `&` for multiple conditions.
- You used string methods like `.str.starts_with()` to filter data based on string matching.

## Selecting Columns

- You used `.select()` to subset columns by passing column names directly or using regex patterns.
- You also demonstrated how to exclude columns with `.select(pl.exclude())`.

### Counting by Group

You can count by group with `.groupby()`:

```python
penguins.groupby("island").count()

## Using Selectors

- The `polars.selectors` module allows you to select columns based on patterns (e.g., columns starting with a prefix using `starts_with()`) or data types (e.g., selecting numeric columns with `by_dtype()`).

## Creating New Columns

- You used `.with_columns()` to create a new boolean column `is_chinstrap` based on a condition (`species == "Chinstrap"`).
