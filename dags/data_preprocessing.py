import pandas as pd

DATA_PATH = "/opt/airflow/data/salesorder.csv"
OUTPUT_PATH = "/opt/airflow/data/salesorder_cleaned.csv"

def clean_dataset():
    df = pd.read_csv(DATA_PATH, sep="\t")

    print("Original rows:", len(df))

    # ---------------- CLEANING ----------------

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Convert date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Remove null dates
    df = df.dropna(subset=["date"])

    # Ensure numeric columns
    df["profit"] = pd.to_numeric(df["profit"], errors="coerce")
    df["totalprice"] = pd.to_numeric(df["totalprice"], errors="coerce")
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")

    # ---------------- NEW COLUMNS ----------------

    # Profit Margin %
    df["profit_margin"] = (df["profit"] / df["totalprice"]) * 100

    # Order Year
    df["order_year"] = df["date"].dt.year

    # Order Month
    df["order_month"] = df["date"].dt.month

    print("Cleaned rows:", len(df))

    # Save cleaned dataset
    df.to_csv(OUTPUT_PATH, index=False)

    print("Cleaned file saved as salesorder_cleaned.csv")


if __name__ == "__main__":
    clean_dataset()