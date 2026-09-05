import pandas as pd

from src.analytics import (
    product_sales_summary,
    inventory_demand_analysis,
    store_sales,
    sales_trends,
)


def build_evidence_documents(data):
    """
    Build grounded evidence documents for RetailIQ retrieval.

    All calculations come from the deterministic analytics
    layer so that retrieved evidence matches the numbers
    used elsewhere in the application.
    """

    products = data["products"]
    sales = data["sales"]
    inventory = data["inventory"]
    stores = data["stores"]

    documents = []

    # ---------------------------------------------------------
    # 1. Overall sales summary
    # ---------------------------------------------------------

    sales_copy = sales.copy()
    sales_copy["date"] = pd.to_datetime(
        sales_copy["date"]
    )

    total_units = int(
        sales_copy["quantity"].sum()
    )

    total_revenue = float(
        (
            sales_copy["quantity"]
            * sales_copy["unit_price"]
        ).sum()
    )

    transaction_count = len(sales_copy)

    earliest_date = sales_copy["date"].min()
    latest_date = sales_copy["date"].max()

    documents.append({
        "doc_id": "overall_sales",
        "category": "sales_summary",
        "text": (
            "Retail sales summary for the available period. "
            f"Total units sold: {total_units}. "
            f"Total revenue: {total_revenue:.2f}. "
            f"Number of sales records: {transaction_count}. "
            f"Sales period: "
            f"{earliest_date.strftime('%Y-%m-%d')} to "
            f"{latest_date.strftime('%Y-%m-%d')}."
        )
    })

    # ---------------------------------------------------------
    # 2. Product sales evidence
    # ---------------------------------------------------------

    product_summary = product_sales_summary(
        sales,
        products
    )

    for _, row in product_summary.iterrows():
        documents.append({
            "doc_id": (
                f"product_sales_{row['product_id']}"
            ),
            "category": "product_sales",
            "text": (
                f"Sales performance for "
                f"{row['product_name']} "
                f"({row['product_id']}). "
                f"Category: {row['category']}. "
                f"Units sold: "
                f"{int(row['units_sold'])}. "
                f"Revenue: "
                f"{float(row['revenue']):.2f}."
            )
        })

    # ---------------------------------------------------------
    # 3. Inventory demand evidence
    # ---------------------------------------------------------

    inventory_summary = inventory_demand_analysis(
        inventory,
        sales,
        products
    )

    for _, row in inventory_summary.iterrows():

        if pd.isna(row["estimated_days_of_stock"]):
            days_of_stock = "not available"
        else:
            days_of_stock = (
                f"{float(row['estimated_days_of_stock']):.1f}"
            )

        documents.append({
            "doc_id": (
                f"inventory_"
                f"{row['store_id']}_"
                f"{row['product_id']}"
            ),
            "category": "inventory",
            "text": (
                f"Inventory status for "
                f"{row['product_name']} "
                f"({row['product_id']}) at store "
                f"{row['store_id']}. "
                f"Current stock: "
                f"{int(row['current_stock'])}. "
                f"Reorder level: "
                f"{int(row['reorder_level'])}. "
                f"Estimated average daily demand: "
                f"{float(row['avg_daily_demand']):.2f} units. "
                f"Estimated days of stock: "
                f"{days_of_stock}."
            )
        })

    # ---------------------------------------------------------
    # 4. Store sales evidence
    # ---------------------------------------------------------

    store_summary = store_sales(
        sales,
        stores
    )

    for _, row in store_summary.iterrows():
        documents.append({
            "doc_id": (
                f"store_sales_{row['store_id']}"
            ),
            "category": "store_sales",
            "text": (
                f"Sales performance for "
                f"{row['store_name']} "
                f"({row['store_id']}) in "
                f"{row['city']}. "
                f"Units sold: "
                f"{int(row['units_sold'])}. "
                f"Revenue: "
                f"{float(row['revenue']):.2f}. "
                f"Transactions: "
                f"{int(row['transactions'])}."
            )
        })

    # ---------------------------------------------------------
    # 5. Sales trend evidence
    # ---------------------------------------------------------

    trend_summary = sales_trends(
        sales,
        products
    )

    for _, row in trend_summary.iterrows():

        if pd.isna(row["change_percent"]):
            change_text = "change percentage unavailable"
        else:
            change_text = (
                f"sales changed by "
                f"{float(row['change_percent']):.2f}%"
            )

        documents.append({
            "doc_id": (
                f"sales_trend_{row['product_id']}"
            ),
            "category": "sales_trend",
            "text": (
                f"Sales trend for "
                f"{row['product_name']} "
                f"({row['product_id']}). "
                f"Recent 7-day average sales: "
                f"{float(row['recent_7_day_avg']):.2f} units. "
                f"Previous 7-day average sales: "
                f"{float(row['previous_7_day_avg']):.2f} units. "
                f"{change_text}. "
                f"Trend classification: "
                f"{row['trend']}."
            )
        })

    return documents


if __name__ == "__main__":
    from src.data_loader import load_all_data

    data = load_all_data()

    documents = build_evidence_documents(data)

    print(
        "Evidence document generation successful!"
    )

    print(
        f"Number of documents: {len(documents)}"
    )

    print("\nFirst 5 evidence documents:\n")

    for document in documents[:5]:
        print(
            f"ID: {document['doc_id']}"
        )
        print(
            f"Category: {document['category']}"
        )
        print(
            f"Text: {document['text']}"
        )
        print("-" * 80)