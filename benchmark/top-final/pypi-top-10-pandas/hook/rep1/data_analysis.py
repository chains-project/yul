import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    df = df.dropna(how="all")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return df.describe(include="all")


def analyze_csv(path: str) -> pd.DataFrame:
    df = load_csv(path)
    df = clean(df)
    return summarize(df)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("usage: python data_analysis.py <csv_path>")
        raise SystemExit(1)

    print(analyze_csv(sys.argv[1]))
