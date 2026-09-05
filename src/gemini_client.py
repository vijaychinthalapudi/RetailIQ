import os
from google import genai


def create_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


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
    Generate a grounded business answer.

    Gemini is responsible for reasoning and language
    generation only. Business numbers must come from
    the supplied evidence.
    """

    client = create_client()

    prompt = f"""
You are RetailIQ, an AI sales and inventory copilot
for a small retail business.

Answer the manager's question using ONLY the business
evidence supplied below.

STRICT GROUNDING RULES:

1. Never invent a number, date, product, store,
   trend, recommendation, or business fact.

2. Do not calculate new business facts that are not
   supported by the evidence.

3. Treat the deterministic evidence as the source
   of truth.

4. The retrieved evidence is supporting evidence.
   Do not contradict it.

5. If the available evidence is insufficient to answer
   the question, explicitly say that the available data
   is insufficient.

6. Never claim that a product WILL definitely run out.
   Use language such as "likely", "expected", or
   "estimated".

7. Recommendations must be based on the supplied evidence.

8. Keep the response concise and useful to a retail manager.

9. Mention the actual product/store names and numbers
   when relevant.

10. Include an "Evidence" section at the end.

11. In the Evidence section, cite the supplied evidence
    using the document identifiers inside square brackets.
    Example:
    [Inventory Evidence] or [inventory_S001_P008]

12. Do not mention Gemini, embeddings, vector databases,
    retrieval, prompts, or internal implementation details.

RESPONSE FORMAT:

Direct answer:
<answer>

Supporting evidence:
- <important number or fact>
- <important number or fact>

Recommended action:
<practical action>

Evidence:
- [document_id or evidence label]
- [document_id or evidence label]

BUSINESS EVIDENCE:
{context}

MANAGER QUESTION:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text