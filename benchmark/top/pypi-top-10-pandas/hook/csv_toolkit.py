import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    df = df.dropna(how="all")
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return df.describe(include="all")


def analyze_csv(path: str) -> pd.DataFrame:
    return summarize(clean(load_csv(path)))
