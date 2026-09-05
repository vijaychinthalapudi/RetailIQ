import pandas as pd


def generate_inventory_recommendations(inventory_analysis):
    """
    Generate deterministic inventory recommendations
    based on estimated days of stock.
    """

    recommendations = []

    for _, row in inventory_analysis.iterrows():
        days = row["estimated_days_of_stock"]

        if pd.isna(days):
            continue

        if days <= 3:
            priority = "CRITICAL"
            action = "Reorder immediately"
        elif days <= 7:
            priority = "HIGH"
            action = "Reorder soon"
        elif days >= 60:
            priority = "LOW"
            action = "Review for overstock"
        else:
            priority = "NORMAL"
            action = "Inventory level is healthy"

        recommendations.append({
            "store_id": row["store_id"],
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "priority": priority,
            "current_stock": int(row["current_stock"]),
            "avg_daily_demand": round(
                row["avg_daily_demand"], 2
            ),
            "estimated_days_of_stock": days,
            "recommendation": action
        })

    return pd.DataFrame(recommendations)


def generate_sales_recommendations(sales_trends):
    """
    Generate deterministic recommendations from sales trends.
    """

    recommendations = []

    for _, row in sales_trends.iterrows():

        trend = row["trend"]

        if trend == "SALES SPIKE":
            action = "Increase replenishment and monitor demand closely"
            priority = "HIGH"

        elif trend == "SALES DROP":
            action = "Investigate declining demand before increasing stock"
            priority = "MEDIUM"

        else:
            action = "Continue monitoring sales"
            priority = "NORMAL"

        recommendations.append({
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "trend": trend,
            "change_percent": row["change_percent"],
            "priority": priority,
            "recommendation": action
        })

    return pd.DataFrame(recommendations)


def generate_all_recommendations(
    inventory_analysis,
    sales_trends
):
    """
    Generate both inventory and sales recommendations.
    """

    inventory_recommendations = generate_inventory_recommendations(
        inventory_analysis
    )

    sales_recommendations = generate_sales_recommendations(
        sales_trends
    )

    return {
        "inventory": inventory_recommendations,
        "sales": sales_recommendations
    }


if __name__ == "__main__":
    from data_loader import load_all_data
    from analytics import (
        sales_trends,
        inventory_demand_analysis
    )

    data = load_all_data()

    inventory_analysis = inventory_demand_analysis(
        data["inventory"],
        data["sales"],
        data["products"]
    )

    trends = sales_trends(
        data["sales"],
        data["products"]
    )

    recommendations = generate_all_recommendations(
        inventory_analysis,
        trends
    )

    print("\n=== INVENTORY RECOMMENDATIONS ===")
    print(
        recommendations["inventory"]
        .sort_values(
            ["priority", "estimated_days_of_stock"]
        )
        .head(20)
        .to_string(index=False)
    )

    print("\n=== SALES RECOMMENDATIONS ===")
    print(
        recommendations["sales"]
        .sort_values("priority")
        .to_string(index=False)
    )