# Challenge 2: CSV Data Processor

A command-line tool to process CSV files with filter, select, and sort operations using pandas.

## Requirements

```bash
pip install pandas
```

## Features

- Filter rows by column values
- Select specific columns
- Sort by column (ascending or descending)
- Chain operations with pipe syntax
- Uses pandas for efficient data processing

## Usage

```bash
python csv_processor.py <file.csv> <query>
```

## Examples

```bash
# Filter people over 28
python csv_processor.py sample_data.csv "filter age > 28"

# Filter and select specific columns
python csv_processor.py sample_data.csv "filter age > 28 | select name,city"

# Filter, select, and sort
python csv_processor.py sample_data.csv "filter age > 28 | select name,city,age | sort age desc"

# Sort by salary
python csv_processor.py sample_data.csv "sort salary desc"
```

## Supported Operators

- `filter <column> <op> <value>` - Filter rows (operators: >, <, ==, !=)
- `select <col1>,<col2>,...` - Select specific columns
- `sort <column> [desc]` - Sort by column (ascending by default)

## Design Focus

- Using pandas library for data manipulation
- Clean class structure
- Modular design
- Error handling
