import json
from pathlib import Path

import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DOCUMENTS_FILE = DATA_DIR / "evidence_documents.json"
EMBEDDINGS_FILE = DATA_DIR / "evidence_embeddings.npy"


def save_index(documents, embeddings):
    """
    Save evidence documents and their embeddings locally.

    The embeddings are generated once using Gemini and then
    reused for future application runs.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(DOCUMENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            documents,
            file,
            indent=2,
            ensure_ascii=False
        )

    np.save(
        EMBEDDINGS_FILE,
        np.asarray(embeddings, dtype=np.float32)
    )

    print("Evidence index saved successfully.")
    print(f"Documents: {DOCUMENTS_FILE}")
    print(f"Embeddings: {EMBEDDINGS_FILE}")


def load_index():
    """
    Load the locally saved evidence index.
    """

    if not DOCUMENTS_FILE.exists():
        raise FileNotFoundError(
            f"Evidence documents not found: {DOCUMENTS_FILE}"
        )

    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"Evidence embeddings not found: {EMBEDDINGS_FILE}"
        )

    with open(DOCUMENTS_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    embeddings = np.load(EMBEDDINGS_FILE)

    if len(documents) != len(embeddings):
        raise ValueError(
            "Evidence documents and embeddings have different sizes."
        )

    return documents, embeddings


def index_exists():
    """
    Check whether the local evidence index already exists.
    """

    return (
        DOCUMENTS_FILE.exists()
        and EMBEDDINGS_FILE.exists()
    )