import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_products():
    return pd.read_csv(DATA_DIR / "products.csv")


def load_stores():
    return pd.read_csv(DATA_DIR / "stores.csv")


def load_inventory():
    return pd.read_csv(DATA_DIR / "inventory.csv")


def load_sales():
    return pd.read_csv(DATA_DIR / "sales.csv")


def load_all_data():
    products = load_products()
    stores = load_stores()
    inventory = load_inventory()
    sales = load_sales()

    return {
        "products": products,
        "stores": stores,
        "inventory": inventory,
        "sales": sales
    }


if __name__ == "__main__":
    data = load_all_data()

    print("Data loading successful!\n")

    for name, df in data.items():
        print(f"{name}: {df.shape[0]} rows × {df.shape[1]} columns")

    print("\nProducts:")
    print(data["products"].head())

    print("\nSales:")
    print(data["sales"].head())