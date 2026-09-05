import csv
import random
from datetime import date, timedelta
from pathlib import Path

# -----------------------------
# SETTINGS
# -----------------------------

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

random.seed(42)

# -----------------------------
# PRODUCTS
# -----------------------------

products = [
    ["P001", "iPhone 15", "Smartphone", 60000],
    ["P002", "Samsung Galaxy S24", "Smartphone", 55000],
    ["P003", "OnePlus 12", "Smartphone", 50000],
    ["P004", "Redmi Note 14", "Smartphone", 18000],
    ["P005", "Dell Inspiron 15", "Laptop", 70000],
    ["P006", "HP Pavilion", "Laptop", 65000],
    ["P007", "Lenovo IdeaPad", "Laptop", 60000],
    ["P008", "Boat Headphones", "Audio", 2000],
    ["P009", "Sony Headphones", "Audio", 8000],
    ["P010", "JBL Bluetooth Speaker", "Audio", 5000],
    ["P011", "Logitech Mouse", "Accessories", 1200],
    ["P012", "HP Wireless Mouse", "Accessories", 1500],
    ["P013", "Mechanical Keyboard", "Accessories", 3500],
    ["P014", "Samsung 24 inch Monitor", "Monitor", 12000],
    ["P015", "LG 27 inch Monitor", "Monitor", 18000],
    ["P016", "Canon Printer", "Printer", 15000],
    ["P017", "Epson Printer", "Printer", 13000],
    ["P018", "TP-Link Router", "Networking", 3000],
    ["P019", "D-Link Router", "Networking", 2500],
    ["P020", "USB-C Cable", "Accessories", 500],
]

# -----------------------------
# STORES
# -----------------------------

stores = [
    ["S001", "Central Store", "Visakhapatnam"],
    ["S002", "Beach Road Store", "Visakhapatnam"],
    ["S003", "MVP Colony Store", "Visakhapatnam"],
    ["S004", "Mangalagiri Store", "Mangalagiri"],
    ["S005", "Vijayawada Store", "Vijayawada"],
]

# -----------------------------
# WRITE PRODUCTS
# -----------------------------

with open(DATA_DIR / "products.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "product_id",
        "product_name",
        "category",
        "price"
    ])

    writer.writerows(products)

# -----------------------------
# WRITE STORES
# -----------------------------

with open(DATA_DIR / "stores.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "store_id",
        "store_name",
        "city"
    ])

    writer.writerows(stores)

# -----------------------------
# INVENTORY
# -----------------------------

inventory = []

for store in stores:
    store_id = store[0]

    for product in products:
        product_id = product[0]

        # Random starting stock
        stock = random.randint(5, 100)

        # Reorder level
        reorder_level = random.randint(10, 30)

        inventory.append([
            store_id,
            product_id,
            stock,
            reorder_level
        ])

# Create a few intentional low-stock products
# so our AI can detect stock-out risks later.

inventory[7][2] = 3
inventory[7][3] = 20

inventory[25][2] = 2
inventory[25][3] = 15

inventory[48][2] = 4
inventory[48][3] = 25

with open(DATA_DIR / "inventory.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "store_id",
        "product_id",
        "current_stock",
        "reorder_level"
    ])

    writer.writerows(inventory)

# -----------------------------
# SALES
# -----------------------------

sales = []

start_date = date(2026, 7, 1)

for day_number in range(60):

    current_date = start_date + timedelta(days=day_number)

    for _ in range(15):

        store = random.choice(stores)
        product = random.choice(products)

        store_id = store[0]
        product_id = product[0]
        price = product[3]

        # Normal sales quantity
        quantity = random.randint(1, 5)

        # Create some intentional sales spikes
        # for Boat Headphones and USB-C Cable.
        if product_id == "P008" and day_number >= 40:
            quantity = random.randint(8, 15)

        if product_id == "P020" and day_number >= 45:
            quantity = random.randint(10, 20)

        # Create some slow-moving products
        if product_id in ["P016", "P017"]:
            quantity = random.randint(0, 1)

        sales.append([
            current_date.isoformat(),
            store_id,
            product_id,
            quantity,
            price
        ])

with open(DATA_DIR / "sales.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "date",
        "store_id",
        "product_id",
        "quantity",
        "unit_price"
    ])

    writer.writerows(sales)

print("Dataset creation completed!")
print()
print("Created files:")
print(" - data/products.csv")
print(" - data/stores.csv")
print(" - data/inventory.csv")
print(" - data/sales.csv")
print()
print(f"Products: {len(products)}")
print(f"Stores: {len(stores)}")
print(f"Inventory records: {len(inventory)}")
print(f"Sales records: {len(sales)}")