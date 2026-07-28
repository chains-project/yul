import argparse
import sys

import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    if path.endswith(".json"):
        return pd.read_json(path)
    return pd.read_csv(path)


def analyze(df: pd.DataFrame) -> None:
    print("Shape:", df.shape)
    print("\nColumns and dtypes:")
    print(df.dtypes)
    print("\nMissing values per column:")
    print(df.isna().sum())
    print("\nSummary statistics:")
    print(df.describe(include="all"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze tabular data with pandas.")
    parser.add_argument("path", help="Path to a CSV or JSON file")
    args = parser.parse_args()

    try:
        df = load_data(args.path)
    except FileNotFoundError:
        print(f"Error: file not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    analyze(df)


if __name__ == "__main__":
    main()
