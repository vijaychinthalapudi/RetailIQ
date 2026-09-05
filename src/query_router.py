def detect_query_intent(question):
    """
    Detect the business intent of a manager's question.

    This is deterministic routing only.
    Gemini is not used for intent detection.
    """

    question_lower = question.lower().strip()

    # Stock-out / low-stock questions
    if any(
        keyword in question_lower
        for keyword in [
            "run out",
            "running out",
            "stock out",
            "stock-out",
            "low stock",
            "low-stock",
            "shortage",
            "reorder",
            "replenish",
            "need to restock",
        ]
    ):
        return "stock_out"

    # Overstock questions
    if any(
        keyword in question_lower
        for keyword in [
            "overstock",
            "over stocked",
            "over-stocked",
            "excess stock",
            "too much stock",
            "slow moving",
            "slow-moving",
            "non-moving",
            "not selling",
        ]
    ):
        return "overstock"

    # Sales trend questions
    if any(
        keyword in question_lower
        for keyword in [
            "trend",
            "trending",
            "spike",
            "spikes",
            "drop",
            "drops",
            "declining",
            "increase",
            "decrease",
            "growing",
            "declining sales",
        ]
    ):
        return "sales_trend"

    # Top-selling / sales performance
    if any(
        keyword in question_lower
        for keyword in [
            "top selling",
            "top-selling",
            "best selling",
            "best-selling",
            "highest sales",
            "most sold",
            "sales performance",
            "sales this month",
            "sold this month",
        ]
    ):
        return "sales_performance"

    # Store-related questions
    if any(
        keyword in question_lower
        for keyword in [
            "store",
            "stores",
            "branch",
            "branches",
        ]
    ):
        return "store_performance"

    # Product-specific questions
    if any(
        keyword in question_lower
        for keyword in [
            "product",
            "products",
            "item",
            "items",
        ]
    ):
        return "product_analysis"

    return "general"