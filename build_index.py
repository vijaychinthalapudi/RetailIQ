from src.data_loader import load_all_data
from src.context_builder import build_evidence_documents
from src.embedding_client import embed_documents
from src.index_manager import save_index


def main():
    print("========================================")
    print("RetailIQ Evidence Index Builder")
    print("========================================")

    print("\n1. Loading business data...")
    data = load_all_data()

    print("Data loaded successfully.")

    print("\n2. Building evidence documents...")
    documents = build_evidence_documents(data)

    print(
        f"Created {len(documents)} evidence documents."
    )

    texts = [
        document["text"]
        for document in documents
    ]

    print("\n3. Creating Gemini embeddings...")
    print(
        "This is a one-time operation."
    )
    print(
        "The process may pause between batches "
        "to respect the embedding quota."
    )

    embeddings = embed_documents(texts)

    print(
        f"\nEmbedding shape: {embeddings.shape}"
    )

    print("\n4. Saving local evidence index...")
    save_index(
        documents,
        embeddings
    )

    print("\n========================================")
    print("Index creation completed successfully!")
    print("========================================")


if __name__ == "__main__":
    main()