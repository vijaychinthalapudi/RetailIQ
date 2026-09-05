import pandas as pd


def get_stock_out_message(days_of_stock, stock_out_date):
    """Convert estimated stock days into a human-readable warning."""

    if pd.isna(days_of_stock) or pd.isna(stock_out_date):
        return "Stock-out timing cannot be estimated from the available data."

    days = float(days_of_stock)

    if days <= 1:
        return "Likely to run out today"
    elif days <= 2:
        return f"Likely to run out tomorrow ({stock_out_date.strftime('%d %b %Y')})"
    elif days <= 7:
        return f"Urgent replenishment required by {stock_out_date.strftime('%d %b %Y')}"
    elif days <= 30:
        return f"Stock expected to last until {stock_out_date.strftime('%d %b %Y')}"
    else:
        return f"Stock expected to last until {stock_out_date.strftime('%d %b %Y')}"


def generate_inventory_recommendations(inventory_analysis, reference_date=None):
    """
    Generate deterministic inventory recommendations.

    reference_date:
        Date from which stock-out dates are calculated.
        If not provided, today's date is used.
    """

    recommendations = []

    if reference_date is None:
        reference_date = pd.Timestamp.today().normalize()
    else:
        reference_date = pd.Timestamp(reference_date).normalize()

    for _, row in inventory_analysis.iterrows():

        days = row["estimated_days_of_stock"]

        if pd.isna(days):
            continue

        days = float(days)

        # Calculate expected stock-out date
        stock_out_date = reference_date + pd.Timedelta(days=days)

        # Determine priority and action
        if days <= 1:
            priority = "CRITICAL"
            action = "Reorder immediately"
        elif days <= 3:
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

        # Human-readable stock situation
        stock_message = get_stock_out_message(
            days,
            stock_out_date
        )

        recommendations.append({
            "store_id": row["store_id"],
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "priority": priority,
            "current_stock": int(row["current_stock"]),
            "avg_daily_demand": round(row["avg_daily_demand"], 2),
            "estimated_days_of_stock": round(days, 1),
            "expected_stock_out_date": stock_out_date.strftime("%Y-%m-%d"),
            "stock_status": stock_message,
            "recommendation": action
        })

    return pd.DataFrame(recommendations)


def generate_sales_recommendations(sales_trends):
    """Generate deterministic recommendations from sales trends."""

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
    sales_trends,
    reference_date=None
):
    """Generate all deterministic business recommendations."""

    inventory_recommendations = generate_inventory_recommendations(
        inventory_analysis,
        reference_date
    )

    sales_recommendations = generate_sales_recommendations(
        sales_trends
    )

    return {
        "inventory": inventory_recommendations,
        "sales": sales_recommendations
    }
