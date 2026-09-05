import os
import time

from google import genai
from google.genai import types
import numpy as np


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


def create_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def normalize_embeddings(embeddings):
    """
    Normalize embedding vectors so cosine similarity
    can be calculated using a simple dot product.
    """

    vectors = np.asarray(
        embeddings,
        dtype=np.float32
    )

    norms = np.linalg.norm(
        vectors,
        axis=1,
        keepdims=True
    )

    norms[norms == 0] = 1.0

    return vectors / norms


def embed_documents(texts):
    """
    Create embeddings for business evidence documents.

    Gemini's free-tier embedding quota limits the number
    of embedding inputs that can be processed in a short
    period, so documents are processed in batches.

    The function waits between batches so the quota window
    can reset.
    """

    if not texts:
        return np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32
        )

    client = create_client()

    batch_size = 100
    all_embeddings = []

    total_documents = len(texts)

    for start in range(
        0,
        total_documents,
        batch_size
    ):

        batch = texts[
            start:start + batch_size
        ]

        print(
            f"Embedding documents "
            f"{start + 1}-{start + len(batch)} "
            f"of {total_documents}..."
        )

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSION
            )
        )

        batch_embeddings = [
            item.values
            for item in response.embeddings
        ]

        all_embeddings.extend(
            batch_embeddings
        )

        # Wait before the next batch so that the
        # free-tier embedding quota can reset.
        if start + len(batch) < total_documents:
            print(
                "\nEmbedding quota window reached."
            )
            print(
                "Waiting 65 seconds before the next batch..."
            )

            time.sleep(65)

    return normalize_embeddings(
        all_embeddings
    )


def embed_query(question):
    """
    Create an embedding for a manager's question.
    """

    client = create_client()

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIMENSION
        )
    )

    embedding = np.asarray(
        response.embeddings[0].values,
        dtype=np.float32
    )

    norm = np.linalg.norm(embedding)

    if norm != 0:
        embedding = embedding / norm

    return embedding