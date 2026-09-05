import pandas as pd

from src.analytics import (
    product_sales_summary,
    inventory_demand_analysis,
    store_sales,
    sales_trends,
)
from src.business_rules import (
    generate_inventory_recommendations,
    generate_sales_recommendations,
)


def build_deterministic_evidence(data):
    """
    Build business evidence from deterministic analytics.

    This function is the source of truth for RetailIQ.
    Gemini should reason only over this evidence.
    """

    products = data["products"]
    stores = data["stores"]
    inventory = data["inventory"]
    sales = data["sales"]

    sales_copy = sales.copy()
    sales_copy["date"] = pd.to_datetime(
        sales_copy["date"]
    )

    reference_date = sales_copy["date"].max()

    # --------------------------------------------------
    # Product sales
    # --------------------------------------------------

    product_summary = product_sales_summary(
        sales,
        products
    )

    # --------------------------------------------------
    # Inventory analysis
    # --------------------------------------------------

    inventory_analysis = inventory_demand_analysis(
        inventory,
        sales,
        products
    )

    inventory_recommendations = (
        generate_inventory_recommendations(
            inventory_analysis,
            reference_date=reference_date
        )
    )

    # --------------------------------------------------
    # Sales trends
    # --------------------------------------------------

    trends = sales_trends(
        sales,
        products
    )

    sales_recommendations = (
        generate_sales_recommendations(
            trends
        )
    )

    # --------------------------------------------------
    # Store performance
    # --------------------------------------------------

    store_summary = store_sales(
        sales,
        stores
    )

    # --------------------------------------------------
    # Overall summary
    # --------------------------------------------------

    total_units = int(
        sales_copy["quantity"].sum()
    )

    total_revenue = float(
        (
            sales_copy["quantity"]
            * sales_copy["unit_price"]
        ).sum()
    )

    return {
        "reference_date": reference_date,
        "total_units": total_units,
        "total_revenue": total_revenue,
        "product_summary": product_summary,
        "inventory_analysis": inventory_analysis,
        "inventory_recommendations": inventory_recommendations,
        "trends": trends,
        "sales_recommendations": sales_recommendations,
        "store_summary": store_summary,
    }


def format_evidence_for_question(
    evidence,
    intent,
    retrieved_documents=None,
):
    """
    Convert deterministic evidence plus retrieved evidence
    into a compact context for Gemini.
    """

    sections = []

    reference_date = evidence["reference_date"]

    sections.append(
        "REFERENCE DATE: "
        f"{reference_date.strftime('%Y-%m-%d')}"
    )

    sections.append(
        "\nOVERALL BUSINESS SUMMARY:\n"
        f"Total units sold: {evidence['total_units']}\n"
        f"Total revenue: {evidence['total_revenue']:.2f}"
    )

    # --------------------------------------------------
    # Stock-out evidence
    # --------------------------------------------------

    if intent == "stock_out":

        recommendations = (
            evidence["inventory_recommendations"]
        )

        critical = recommendations[
            recommendations["priority"].isin(
                ["CRITICAL", "HIGH"]
            )
        ]

        if not critical.empty:
            sections.append(
                "\nSTOCK-OUT / REPLENISHMENT EVIDENCE:"
            )

            for _, row in critical.iterrows():
                sections.append(
                    f"[Inventory Evidence] "
                    f"{row['product_name']} "
                    f"({row['product_id']}) at "
                    f"{row['store_id']}: "
                    f"current stock {row['current_stock']}, "
                    f"average daily demand "
                    f"{row['avg_daily_demand']:.2f}, "
                    f"estimated days of stock "
                    f"{row['estimated_days_of_stock']:.1f}, "
                    f"expected stock-out date "
                    f"{row['expected_stock_out_date']}, "
                    f"priority {row['priority']}, "
                    f"action: {row['recommendation']}."
                )

    # --------------------------------------------------
    # Overstock evidence
    # --------------------------------------------------

    elif intent == "overstock":

        recommendations = (
            evidence["inventory_recommendations"]
        )

        overstock = recommendations[
            recommendations["priority"] == "LOW"
        ]

        if not overstock.empty:
            sections.append(
                "\nOVERSTOCK EVIDENCE:"
            )

            for _, row in overstock.iterrows():
                sections.append(
                    f"[Inventory Evidence] "
                    f"{row['product_name']} "
                    f"({row['product_id']}) at "
                    f"{row['store_id']}: "
                    f"current stock {row['current_stock']}, "
                    f"average daily demand "
                    f"{row['avg_daily_demand']:.2f}, "
                    f"estimated days of stock "
                    f"{row['estimated_days_of_stock']:.1f}, "
                    f"action: {row['recommendation']}."
                )

    # --------------------------------------------------
    # Sales performance
    # --------------------------------------------------

    elif intent == "sales_performance":

        summary = evidence["product_summary"].copy()

        summary = summary.sort_values(
            "units_sold",
            ascending=False
        ).head(10)

        sections.append(
            "\nTOP PRODUCT SALES EVIDENCE:"
        )

        for _, row in summary.iterrows():
            sections.append(
                f"[Product Sales Evidence] "
                f"{row['product_name']} "
                f"({row['product_id']}): "
                f"{int(row['units_sold'])} units sold, "
                f"revenue {float(row['revenue']):.2f}."
            )

    # --------------------------------------------------
    # Sales trends
    # --------------------------------------------------

    elif intent == "sales_trend":

        trends = evidence["trends"]

        sections.append(
            "\nSALES TREND EVIDENCE:"
        )

        for _, row in trends.iterrows():
            if pd.isna(row["change_percent"]):
                change = "change unavailable"
            else:
                change = (
                    f"{float(row['change_percent']):.2f}%"
                )

            sections.append(
                f"[Trend Evidence] "
                f"{row['product_name']} "
                f"({row['product_id']}): "
                f"recent 7-day average "
                f"{float(row['recent_7_day_avg']):.2f}, "
                f"previous 7-day average "
                f"{float(row['previous_7_day_avg']):.2f}, "
                f"change {change}, "
                f"classification {row['trend']}."
            )

    # --------------------------------------------------
    # Store performance
    # --------------------------------------------------

    elif intent == "store_performance":

        stores = evidence["store_summary"].copy()

        stores = stores.sort_values(
            "revenue",
            ascending=False
        )

        sections.append(
            "\nSTORE PERFORMANCE EVIDENCE:"
        )

        for _, row in stores.iterrows():
            sections.append(
                f"[Store Evidence] "
                f"{row['store_name']} "
                f"({row['store_id']}) in "
                f"{row['city']}: "
                f"{int(row['units_sold'])} units sold, "
                f"revenue {float(row['revenue']):.2f}, "
                f"{int(row['transactions'])} transactions."
            )

    # --------------------------------------------------
    # Retrieved semantic evidence
    # --------------------------------------------------

    if retrieved_documents:
        sections.append(
            "\nRETRIEVED EVIDENCE:"
        )

        for document in retrieved_documents:
            sections.append(
                f"[{document['doc_id']}] "
                f"{document['text']}"
            )

    return "\n".join(sections)