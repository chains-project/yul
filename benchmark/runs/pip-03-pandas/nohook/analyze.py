import argparse
import sys

import pandas as pd


def analyze(csv_path: str) -> None:
    df = pd.read_csv(csv_path, parse_dates=["date"])

    print("=== Shape ===")
    print(df.shape)

    print("\n=== Columns & dtypes ===")
    print(df.dtypes)

    print("\n=== Summary statistics ===")
    print(df.describe(include="all"))

    print("\n=== Revenue by region ===")
    print(df.groupby("region")["revenue"].sum().sort_values(ascending=False))

    print("\n=== Revenue by product ===")
    print(df.groupby("product")["revenue"].sum().sort_values(ascending=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze tabular data with pandas.")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="sample_data.csv",
        help="Path to a CSV file to analyze (default: sample_data.csv)",
    )
    args = parser.parse_args()
    analyze(args.csv_path)


if __name__ == "__main__":
    sys.exit(main())
