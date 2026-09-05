from flask import Flask, jsonify, request, send_from_directory

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


app = Flask(
    __name__,
    static_folder="frontend"
)


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
# Routes
# --------------------------------------------------

@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory("frontend", filename)


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "RetailIQ",
        "evidence_index_loaded": retriever is not None
    })


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

        # ------------------------------------------
        # 5. Return answer
        # ------------------------------------------

        return jsonify({
            "answer": answer,
            "intent": intent
        })

    except Exception as error:

        print(
            f"ERROR while processing question: {error}"
        )

        return jsonify({
            "error": str(error)
        }), 500


# --------------------------------------------------
# Start application
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========================================")
    print("RetailIQ is starting...")
    print("========================================")
    print("Open: http://localhost:8000")
    print("========================================\n")

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )