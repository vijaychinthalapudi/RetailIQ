from flask import Flask, request, jsonify, send_from_directory
import sys
from pathlib import Path

# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
FRONTEND_DIR = BASE_DIR / "frontend"

sys.path.append(str(SRC_DIR))


# --------------------------------------------------
# Import RetailIQ modules
# --------------------------------------------------

from data_loader import load_all_data
from analytics import (
    inventory_demand_analysis,
    sales_trends
)
from business_rules import generate_all_recommendations
from gemini_client import ask_gemini


# --------------------------------------------------
# Flask application
# --------------------------------------------------

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)


# --------------------------------------------------
# Load and analyse business data
# --------------------------------------------------

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


# --------------------------------------------------
# Build grounded business context for Gemini
# --------------------------------------------------

def build_business_context():
    """
    Build a factual context from the retail data.

    Gemini receives only information calculated from
    the application's own business data.
    """

    context_parts = []

    # -------------------------------
    # Sales overview
    # -------------------------------

    total_units = int(data["sales"]["quantity"].sum())

    total_revenue = (
        data["sales"]["quantity"] *
        data["sales"]["unit_price"]
    ).sum()

    transaction_count = len(data["sales"])

    context_parts.append(
        f"""
OVERALL SALES:
Total units sold: {total_units}
Total revenue: {total_revenue:,.0f}
Number of sales records: {transaction_count}
"""
    )

    # -------------------------------
    # Product sales
    # -------------------------------

    product_sales = (
        data["sales"]
        .groupby("product_id")["quantity"]
        .sum()
        .reset_index()
        .merge(
            data["products"],
            on="product_id",
            how="left"
        )
        .sort_values("quantity", ascending=False)
    )

    product_lines = []

    for _, row in product_sales.iterrows():
        product_lines.append(
            f"- {row['product_name']}: "
            f"{int(row['quantity'])} units sold"
        )

    context_parts.append(
        "\nPRODUCT SALES:\n" +
        "\n".join(product_lines)
    )

    # -------------------------------
    # Inventory recommendations
    # -------------------------------

    inventory_recommendations = recommendations["inventory"]

    inventory_lines = []

    for _, row in inventory_recommendations.iterrows():

        inventory_lines.append(
            f"""
- Product: {row['product_name']}
  Store: {row['store_id']}
  Current stock: {row['current_stock']} units
  Average daily demand: {row['avg_daily_demand']} units
  Priority: {row['priority']}
  Stock status: {row['stock_status']}
  Recommendation: {row['recommendation']}
"""
        )

    context_parts.append(
        "\nINVENTORY STATUS AND RECOMMENDATIONS:\n" +
        "\n".join(inventory_lines)
    )

    # -------------------------------
    # Sales trends
    # -------------------------------

    trend_lines = []

    for _, row in trends.iterrows():

        trend_lines.append(
            f"""
- {row['product_name']}
  Sales trend: {row['trend']}
  Change: {row['change_percent']}%
"""
        )

    context_parts.append(
        "\nSALES TRENDS:\n" +
        "\n".join(trend_lines)
    )

    # -------------------------------
    # Non-moving products
    # -------------------------------

    non_moving = recommendations.get("non_moving")

    if non_moving is not None and not non_moving.empty:

        non_moving_lines = []

        for _, row in non_moving.iterrows():
            non_moving_lines.append(
                f"- {row['product_name']}: "
                f"{row['total_units']} units sold"
            )

        context_parts.append(
            "\nNON-MOVING PRODUCTS:\n" +
            "\n".join(non_moving_lines)
        )
    else:
        context_parts.append(
            "\nNON-MOVING PRODUCTS:\n"
            "No non-moving products were identified."
        )

    return "\n".join(context_parts)


# --------------------------------------------------
# Frontend
# --------------------------------------------------

@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "application": "RetailIQ"
    })


# --------------------------------------------------
# Ask RetailIQ
# --------------------------------------------------

@app.route("/ask", methods=["POST"])
def ask():

    try:
        request_data = request.get_json(silent=True) or {}

        question = request_data.get(
            "question",
            ""
        ).strip()

        if not question:
            return jsonify({
                "error": "Please enter a question."
            }), 400

        context = build_business_context()

        answer = ask_gemini(
            context,
            question
        )

        return jsonify({
            "question": question,
            "answer": answer
        })

    except Exception as error:

        print("Application error:", error)

        return jsonify({
            "error": (
                "RetailIQ could not process the request. "
                "Please try again."
            )
        }), 500


# --------------------------------------------------
# Start application
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("RetailIQ - Sales and Inventory Copilot")
    print("=" * 50)
    print("Application: http://localhost:8000")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )