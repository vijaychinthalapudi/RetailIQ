import os
from google import genai


def create_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(
        api_key=api_key
    )


def ask_gemini(context, question):
    """
    Generate a concise, grounded manager summary.

    Gemini is responsible only for natural-language
    reasoning and summarization.

    Deterministic analytics remain the source of truth
    for numbers, dates, trends, inventory status,
    and recommendations.
    """

    client = create_client()

    prompt = f"""
You are RetailIQ, an AI sales and inventory copilot
for a small retail business.

Answer the manager's question using ONLY the business
evidence supplied below.

STRICT GROUNDING RULES:

1. Never invent numbers, dates, products, stores,
   trends, recommendations, or business facts.

2. Treat the deterministic business evidence as the
   source of truth.

3. Do not calculate new business facts that are not
   directly supported by the supplied evidence.

4. Never contradict the supplied evidence.

5. If the available evidence is insufficient to answer
   the question, clearly say that the available data
   is insufficient.

6. Never say a product WILL definitely run out.
   Use terms such as "likely", "expected", or
   "estimated" when discussing stock-outs.

7. Any recommendation must be supported by the
   supplied evidence.

8. Mention actual product or store names and important
   numbers when they are directly relevant.

9. Do not mention Gemini, prompts, embeddings,
   vector databases, retrieval systems, or internal
   implementation details.

10. The detailed evidence and business cards are already
    displayed separately by the application.

OUTPUT RULES:

- Return ONLY a concise manager summary.
- Use 1 to 3 sentences.
- Keep the response below 60 words whenever possible.
- Do NOT use headings.
- Do NOT use bullet points.
- Do NOT create an Evidence section.
- Do NOT create a Supporting evidence section.
- Do NOT create a Recommended action section.
- Do NOT repeat the full evidence supplied below.
- Focus on the most important answer and practical
  implication for the manager.

BUSINESS EVIDENCE:
{context}

MANAGER QUESTION:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()