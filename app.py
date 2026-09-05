from flask import Flask, jsonify, request, send_from_directory
import pandas as pd

from src.data_loader import load_all_data
from src.analytics import (
    inventory_demand_analysis,
    sales_trends,
)
from src.business_rules import generate_all_recommendations
from src.query_router import detect_query_intent
from src.evidence_builder import (
    build_deterministic_evidence,
    format_evidence_for_question,
)
from src.index_manager import load_index, index_exists
from src.retriever import EvidenceRetriever
from src.gemini_client import ask_gemini


# --------------------------------------------------
# Flask application
# --------------------------------------------------

app = Flask(
    __name__,
    static_folder="frontend"
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def money(value):
    """Format revenue for dashboard display."""
    value = float(value)

    if value >= 10_000_000:
        return f"₹{value / 10_000_000:.2f}Cr"

    elif value >= 100_000:
        return f"₹{value / 100_000:.2f}L"

    else:
        return f"₹{value:,.0f}"


# --------------------------------------------------
# Load business data
# --------------------------------------------------

print("Loading RetailIQ business data...")

data = load_all_data()

print("Business data loaded successfully.")


# --------------------------------------------------
# Build deterministic analytics
# --------------------------------------------------

inventory_analysis = inventory_demand_analysis(
    data["inventory"],
    data["sales"],
    data["products"]
)

trends = sales_trends(
    data["sales"],
    data["products"]
)

reference_date = data["sales"]["date"].max()

recommendations = generate_all_recommendations(
    inventory_analysis,
    trends,
    reference_date=reference_date
)


# --------------------------------------------------
# Load local evidence index
# --------------------------------------------------

retriever = None

if index_exists():

    print("Loading saved evidence index...")

    documents, embeddings = load_index()

    retriever = EvidenceRetriever(
        documents,
        embeddings
    )

    print(
        f"Evidence index loaded: "
        f"{len(documents)} documents"
    )

else:

    print(
        "WARNING: Evidence index not found."
    )


# --------------------------------------------------
# Build deterministic evidence
# --------------------------------------------------

print("Building deterministic business evidence...")

deterministic_evidence = build_deterministic_evidence(
    data
)

print("Business evidence ready.")


# --------------------------------------------------
# Convert deterministic evidence into UI cards
# --------------------------------------------------

def make_cards(intent):
    """
    Convert deterministic business evidence into UI cards.

    Important business numbers and recommendations come
    from deterministic analytics.

    Gemini is used only for the natural-language summary.
    """

    cards = []

    # --------------------------------------------------
    # Stock-out / inventory attention
    # --------------------------------------------------

    if intent == "stock_out":

        df = deterministic_evidence[
            "inventory_recommendations"
        ].copy()

        if df.empty:
            return cards

        df = df[
            df["priority"].isin(
                ["CRITICAL", "HIGH"]
            )
        ]

        df = df.sort_values(
            "estimated_days_of_stock"
        )

        for _, row in df.head(8).iterrows():

            cards.append({
                "title": row["product_name"],

                "priority": row["priority"],

                "main": (
                    f"{int(row['current_stock'])} "
                    f"units in stock"
                ),

                "detail": (
                    f"Average demand: "
                    f"{float(row['avg_daily_demand']):.2f} "
                    f"units/day. "
                    f"Estimated stock remaining: "
                    f"{float(row['estimated_days_of_stock']):.1f} "
                    f"days."
                ),

                "status": (
                    f"Expected stock-out: "
                    f"{row['expected_stock_out_date']} "
                    f"at {row['store_id']}."
                ),

                "action": row["recommendation"]
            })


    # --------------------------------------------------
    # Overstock
    # --------------------------------------------------

    elif intent == "overstock":

        df = deterministic_evidence[
            "inventory_recommendations"
        ].copy()

        df = df[
            df["priority"] == "LOW"
        ]

        df = df.sort_values(
            "estimated_days_of_stock",
            ascending=False
        )

        for _, row in df.head(8).iterrows():

            cards.append({
                "title": row["product_name"],

                "priority": "LOW",

                "main": (
                    f"{int(row['current_stock'])} "
                    f"units in stock"
                ),

                "detail": (
                    f"Average demand: "
                    f"{float(row['avg_daily_demand']):.2f} "
                    f"units/day. "
                    f"Estimated coverage: "
                    f"{float(row['estimated_days_of_stock']):.1f} "
                    f"days."
                ),

                "status": (
                    f"Store: {row['store_id']}"
                ),

                "action": row["recommendation"]
            })


    # --------------------------------------------------
    # Top-selling products
    # --------------------------------------------------

    elif intent == "sales_performance":

        df = deterministic_evidence[
            "product_summary"
        ].copy()

        df = df.sort_values(
            "units_sold",
            ascending=False
        ).head(8)

        for _, row in df.iterrows():

            cards.append({
                "title": row["product_name"],

                "priority": "TOP SELLER",

                "main": (
                    f"{int(row['units_sold'])} "
                    f"units sold"
                ),

                "detail": (
                    f"Revenue: "
                    f"₹{float(row['revenue']):,.0f}"
                ),

                "status": (
                    f"Category: {row['category']}"
                ),

                "action": (
                    "Continue monitoring demand"
                )
            })


    # --------------------------------------------------
    # Sales trends
    # --------------------------------------------------

    elif intent == "sales_trend":

        df = deterministic_evidence[
            "sales_recommendations"
        ].copy()

        df = df[
            df["trend"].isin(
                [
                    "SALES SPIKE",
                    "SALES DROP"
                ]
            )
        ]

        for _, row in df.iterrows():

            change = row["change_percent"]

            if pd.isna(change):

                change_text = "Change unavailable"

            else:

                change_text = (
                    f"{float(change):+.2f}%"
                )

            cards.append({
                "title": row["product_name"],

                "priority": row["priority"],

                "main": (
                    f"{row['trend']}: "
                    f"{change_text}"
                ),

                "detail": (
                    "Recent sales movement compared "
                    "with the previous 7-day period."
                ),

                "status": row["trend"],

                "action": row["recommendation"]
            })


    # --------------------------------------------------
    # Store performance
    # --------------------------------------------------

    elif intent == "store_performance":

        df = deterministic_evidence[
            "store_summary"
        ].copy()

        df = df.sort_values(
            "revenue",
            ascending=False
        ).head(5)

        for _, row in df.iterrows():

            cards.append({
                "title": row["store_name"],

                "priority": "STORE",

                "main": (
                    f"₹{float(row['revenue']):,.0f} "
                    f"revenue"
                ),

                "detail": (
                    f"{int(row['units_sold'])} units sold "
                    f"across {int(row['transactions'])} "
                    f"transactions."
                ),

                "status": (
                    f"Location: {row['city']}"
                ),

                "action": (
                    "Continue monitoring store performance"
                )
            })


    # --------------------------------------------------
    # Generic product question
    # --------------------------------------------------

    elif intent == "product_analysis":

        df = deterministic_evidence[
            "product_summary"
        ].copy()

        df = df.sort_values(
            "units_sold",
            ascending=False
        ).head(8)

        for _, row in df.iterrows():

            cards.append({
                "title": row["product_name"],

                "priority": "PRODUCT",

                "main": (
                    f"{int(row['units_sold'])} "
                    f"units sold"
                ),

                "detail": (
                    f"Revenue: "
                    f"₹{float(row['revenue']):,.0f}. "
                    f"Category: {row['category']}."
                ),

                "action": (
                    "Review product performance"
                )
            })


    return cards


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/")
def home():

    return send_from_directory(
        "frontend",
        "index.html"
    )


@app.route("/<path:filename>")
def frontend_files(filename):

    return send_from_directory(
        "frontend",
        filename
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "service": "RetailIQ",
        "evidence_index_loaded": retriever is not None
    })


# --------------------------------------------------
# Dashboard API
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    sales = data["sales"]

    # Overall sales metrics

    units_sold = int(
        sales["quantity"].sum()
    )

    revenue = float(
        (
            sales["quantity"]
            * sales["unit_price"]
        ).sum()
    )

    # Critical inventory recommendations

    inventory_recommendations = (
        deterministic_evidence[
            "inventory_recommendations"
        ]
    )

    critical_stock = int(
        (
            inventory_recommendations["priority"]
            == "CRITICAL"
        ).sum()
    )

    # Sales spikes

    sales_spikes = int(
        (
            trends["trend"]
            == "SALES SPIKE"
        ).sum()
    )

    return jsonify({

        "units_sold": units_sold,

        "revenue": money(
            revenue
        ),

        "critical_stock": critical_stock,

        "sales_spikes": sales_spikes

    })


# --------------------------------------------------
# Ask RetailIQ
# --------------------------------------------------

@app.route("/ask", methods=["POST"])
def ask():

    try:

        body = request.get_json(
            silent=True
        )

        if not body:

            return jsonify({
                "error": "Request body is missing."
            }), 400

        question = body.get(
            "question",
            ""
        ).strip()

        if not question:

            return jsonify({
                "error": "Please enter a question."
            }), 400


        # ------------------------------------------
        # 1. Detect business intent
        # ------------------------------------------

        intent = detect_query_intent(
            question
        )

        print(
            f"\nQuestion: {question}"
        )

        print(
            f"Detected intent: {intent}"
        )


        # ------------------------------------------
        # 2. Retrieve semantic evidence
        # ------------------------------------------

        retrieved_documents = []

        if retriever is not None:

            retrieved_documents = (
                retriever.search(
                    question,
                    top_k=5
                )
            )


        # ------------------------------------------
        # 3. Build grounded context
        # ------------------------------------------

        context = format_evidence_for_question(
            deterministic_evidence,
            intent,
            retrieved_documents
        )


        # ------------------------------------------
        # 4. Ask Gemini to reason over evidence
        # ------------------------------------------

        answer = ask_gemini(
            context,
            question
        )

        # Gemini's response is used only as a
        # concise manager-facing summary.
        #
        # Detailed numbers, evidence and actions
        # are displayed separately through the
        # deterministic UI cards.

        summary = answer.strip()

        # Remove verbose sections if Gemini happens
        # to return them despite the prompt.
        for section in [
            "Supporting evidence:",
            "Recommended action:",
            "Evidence:"
        ]:
            if section in summary:
                summary = summary.split(
                    section,
                    1
                )[0].strip()

        # Safety fallback if Gemini returns nothing.
        if not summary:
            summary = (
                "The available business data was analyzed "
                "using RetailIQ's deterministic analytics."
            )


        # ------------------------------------------
        # 5. Convert deterministic evidence to cards
        # ------------------------------------------

        cards = make_cards(
            intent
        )


        # ------------------------------------------
        # 6. Return response
        # ------------------------------------------

        return jsonify({

            # IMPORTANT:
            # Return the cleaned summary here,
            # NOT the complete Gemini response.
            "summary": summary,

            # Keep the original answer available
            # for debugging/API consumers.
            "answer": answer,

            "intent": intent,

            "cards": cards,

            "dashboard": {

                "units_sold": int(
                    data["sales"]["quantity"].sum()
                ),

                "revenue": money(
                    (
                        data["sales"]["quantity"]
                        * data["sales"]["unit_price"]
                    ).sum()
                )

            }

        })


    except Exception as error:

        print(
            f"ERROR in /ask: {error}"
        )

        return jsonify({
            "error": str(error)
        }), 500


# --------------------------------------------------
# Start application
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "RetailIQ is starting..."
    )

    print(
        "========================================"
    )

    print(
        "Open: http://localhost:8000"
    )

    print(
        "========================================\n"
    )

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )