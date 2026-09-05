from gemini_client import ask_gemini


context = """
Product: Boat Headphones
Store: S001
Current stock: 3 units
Reorder level: 20 units
Average daily demand: 4.60 units
Estimated days of stock: 0.7 days

Product: USB-C Cable
Sales trend: SALES SPIKE
Change: +90.41%
"""


question = "What products need attention right now?"

answer = ask_gemini(context, question)

print("\n=== RETAILIQ RESPONSE ===")
print(answer)