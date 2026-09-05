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


if __name__ == "__main__":
    from data_loader import load_all_data

    data = load_all_data()

    print("\n=== SALES SUMMARY ===")
    print(sales_summary(data["sales"]))

    print("\n=== TOP PRODUCTS ===")
    print(product_sales_summary(
        data["sales"],
        data["products"]
    ).head(10))

    print("\n=== LOW STOCK ITEMS ===")
    print(low_stock_items(
        data["inventory"],
        data["products"]
    ).head(20))

    print("\n=== STORE PERFORMANCE ===")
    print(store_sales(
        data["sales"],
        data["stores"]
    ))