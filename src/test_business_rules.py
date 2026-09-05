from data_loader import load_all_data
from analytics import inventory_demand_analysis, sales_trends
from business_rules import generate_all_recommendations

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
    recommendations["inventory"][
        [
            "product_name",
            "current_stock",
            "avg_daily_demand",
            "estimated_days_of_stock",
            "expected_stock_out_date",
            "stock_status",
            "recommendation"
        ]
    ].head(10).to_string(index=False)
)