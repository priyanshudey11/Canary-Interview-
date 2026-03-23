import pandas as pd
import sys


class CSVProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.df = None

    def load_data(self):
        try:
            self.df = pd.read_csv(self.filename)
        except FileNotFoundError:
            raise ValueError(f"File not found: {self.filename}")
        except Exception as e:
            raise ValueError(f"Error reading CSV: {e}")

    def filter(self, column, operator, value):
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found")

        try:
            value = float(value)
            if operator == '>':
                self.df = self.df[self.df[column] > value]
            elif operator == '<':
                self.df = self.df[self.df[column] < value]
            elif operator == '==':
                self.df = self.df[self.df[column] == value]
            elif operator == '!=':
                self.df = self.df[self.df[column] != value]
        except ValueError:
            if operator == '==':
                self.df = self.df[self.df[column] == value]
            elif operator == '!=':
                self.df = self.df[self.df[column] != value]

    def select(self, columns):
        missing = [col for col in columns if col not in self.df.columns]
        if missing:
            raise ValueError(f"Columns not found: {', '.join(missing)}")
        self.df = self.df[columns]

    def sort(self, column, descending=False):
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found")
        self.df = self.df.sort_values(by=column, ascending=not descending)

    def get_results(self):
        return self.df


def parse_and_execute(filename, query):
    processor = CSVProcessor(filename)
    processor.load_data()

    parts = query.split('|')

    for part in parts:
        part = part.strip()

        if part.startswith('filter '):
            filter_expr = part[7:].strip()

            for op in ['>', '<', '==', '!=']:
                if op in filter_expr:
                    column, value = filter_expr.split(op)
                    processor.filter(column.strip(), op, value.strip())
                    break

        elif part.startswith('select '):
            columns_str = part[7:].strip()
            columns = [col.strip() for col in columns_str.split(',')]
            processor.select(columns)

        elif part.startswith('sort '):
            sort_expr = part[5:].strip()
            descending = False

            if sort_expr.endswith(' desc'):
                descending = True
                sort_expr = sort_expr[:-5].strip()

            processor.sort(sort_expr, descending)

    return processor.get_results()


def main():
    if len(sys.argv) < 3:
        print("Usage: python csv_processor.py <file.csv> <query>")
        print("Example: python csv_processor.py data.csv \"filter age > 28 | select name,city | sort age desc\"")
        return

    filename = sys.argv[1]
    query = sys.argv[2]

    try:
        results = parse_and_execute(filename, query)

        if results.empty:
            print("No results")
        else:
            print(results.to_csv(index=False))

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
