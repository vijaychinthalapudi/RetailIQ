import pandas as pd


def sales_summary(sales):
    """Calculate overall sales and revenue metrics."""
    total_units = int(sales["quantity"].sum())
    total_revenue = float(
        (sales["quantity"] * sales["unit_price"]).sum()
    )

    return {
        "total_units_sold": total_units,
        "total_revenue": total_revenue,
        "number_of_transactions": len(sales),
    }


def product_sales(sales, products):
    """Calculate sales performance for each product."""
    result = (
        sales.groupby("product_id")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("quantity", lambda x: 0)
        )
        .reset_index()
    )

    # Calculate revenue correctly
    sales_copy = sales.copy()
    sales_copy["revenue"] = (
        sales_copy["quantity"] * sales_copy["unit_price"]
    )

    result = (
        sales_copy.groupby("product_id")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("revenue", "sum")
        )
        .reset_index()
    )

    result = result.merge(
        products[["product_id", "product_name", "category"]],
        on="product_id",
        how="left"
    )

    return result.sort_values("units_sold", ascending=False)


def inventory_status(inventory, products):
    """Identify low-stock and healthy inventory."""
    result = inventory.merge(
        products[["product_id", "product_name", "category"]],
        on="product_id",
        how="left"
    )

    result["stock_status"] = result.apply(
        lambda row: (
            "LOW STOCK"
            if row["current_stock"] <= row["reorder_level"]
            else "HEALTHY"
        ),
        axis=1
    )

    return result


def low_stock_items(inventory, products):
    """Return products that are at or below reorder level."""
    status = inventory_status(inventory, products)

    return status[
        status["stock_status"] == "LOW STOCK"
    ].sort_values("current_stock")


def store_sales(sales, stores):
    """Calculate sales performance by store."""
    sales_copy = sales.copy()
    sales_copy["revenue"] = (
        sales_copy["quantity"] * sales_copy["unit_price"]
    )

    result = (
        sales_copy.groupby("store_id")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("revenue", "sum"),
            transactions=("product_id", "count")
        )
        .reset_index()
    )

    result = result.merge(
        stores[["store_id", "store_name", "city"]],
        on="store_id",
        how="left"
    )

    return result.sort_values("revenue", ascending=False)


def product_sales_summary(sales, products):
    """Create a simple product-level summary."""
    result = product_sales(sales, products)

    return result[
        [
            "product_id",
            "product_name",
            "category",
            "units_sold",
            "revenue"
        ]
    ]


def inventory_summary(inventory, products):
    """Create a simple inventory summary."""
    status = inventory_status(inventory, products)

    return status[
        [
            "store_id",
            "product_id",
            "product_name",
            "category",
            "current_stock",
            "reorder_level",
            "stock_status"
        ]
    ]
def stock_alerts(inventory, products):
    """Classify inventory risk levels."""
    result = inventory.merge(
        products[["product_id", "product_name", "category"]],
        on="product_id",
        how="left"
    )

    def classify(row):
        if row["current_stock"] <= row["reorder_level"] * 0.5:
            return "CRITICAL"
        elif row["current_stock"] <= row["reorder_level"]:
            return "LOW STOCK"
        else:
            return "HEALTHY"

    result["alert_level"] = result.apply(classify, axis=1)

    return result.sort_values(
        ["alert_level", "current_stock"]
    )


def sales_trends(sales, products):
    """Identify sales spikes and drops using daily product sales."""
    sales_copy = sales.copy()
    sales_copy["date"] = pd.to_datetime(sales_copy["date"])

    daily_sales = (
        sales_copy.groupby(["date", "product_id"])["quantity"]
        .sum()
        .reset_index()
    )

    results = []

    for product_id, group in daily_sales.groupby("product_id"):
        group = group.sort_values("date")

        if len(group) < 14:
            continue

        recent = group.tail(7)["quantity"].mean()
        previous = group.iloc[-14:-7]["quantity"].mean()

        if previous == 0:
            change_percent = None
        else:
            change_percent = ((recent - previous) / previous) * 100

        if change_percent is not None and change_percent >= 50:
            trend = "SALES SPIKE"
        elif change_percent is not None and change_percent <= -30:
            trend = "SALES DROP"
        else:
            trend = "STABLE"

        results.append({
            "product_id": product_id,
            "recent_7_day_avg": round(recent, 2),
            "previous_7_day_avg": round(previous, 2),
            "change_percent": (
                round(change_percent, 2)
                if change_percent is not None
                else None
            ),
            "trend": trend
        })

    result = pd.DataFrame(results)

    return result.merge(
        products[["product_id", "product_name", "category"]],
        on="product_id",
        how="left"
    )


def non_moving_products(sales, products, days=60):
    """Identify products with very low sales during the available period."""
    sales_copy = sales.copy()

    product_sales = (
        sales_copy.groupby("product_id")["quantity"]
        .sum()
        .reset_index(name="units_sold")
    )

    result = products.merge(
        product_sales,
        on="product_id",
        how="left"
    )

    result["units_sold"] = result["units_sold"].fillna(0)

    return result[
        result["units_sold"] <= 5
    ].sort_values("units_sold")


def inventory_demand_analysis(inventory, sales, products):
    """Compare current stock with average daily demand."""
    sales_copy = sales.copy()

    total_days = (
        pd.to_datetime(sales_copy["date"]).max()
        - pd.to_datetime(sales_copy["date"]).min()
    ).days + 1

    demand = (
        sales_copy.groupby("product_id")["quantity"]
        .sum()
        .reset_index(name="total_units_sold")
    )

    demand["avg_daily_demand"] = (
        demand["total_units_sold"] / total_days
    )

    result = inventory.merge(
        demand,
        on="product_id",
        how="left"
    )

    result["avg_daily_demand"] = result["avg_daily_demand"].fillna(0)

    result["estimated_days_of_stock"] = result.apply(
        lambda row: (
            round(
                row["current_stock"] / row["avg_daily_demand"],
                1
            )
            if row["avg_daily_demand"] > 0
            else None
        ),
        axis=1
    )

    result = result.merge(
        products[["product_id", "product_name", "category"]],
        on="product_id",
        how="left"
    )

    return result

if __name__ == "__main__":
    from data_loader import load_all_data

    data = load_all_data()

    print("\n=== STOCK ALERTS ===")
    print(
        stock_alerts(
            data["inventory"],
            data["products"]
        ).head(20)
    )

    print("\n=== SALES TRENDS ===")
    print(
        sales_trends(
            data["sales"],
            data["products"]
        )
    )

    print("\n=== NON-MOVING PRODUCTS ===")
    print(
        non_moving_products(
            data["sales"],
            data["products"]
        )
    )

    print("\n=== INVENTORY DEMAND ANALYSIS ===")
    print(
        inventory_demand_analysis(
            data["inventory"],
            data["sales"],
            data["products"]
        ).head(20)
    )