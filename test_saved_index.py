from src.index_manager import load_index
from src.retriever import EvidenceRetriever


def main():
    print("Loading saved RetailIQ evidence index...")

    documents, embeddings = load_index()

    print(f"Documents loaded: {len(documents)}")
    print(f"Embeddings loaded: {embeddings.shape}")

    print("\nCreating retriever...")
    retriever = EvidenceRetriever(
        documents,
        embeddings
    )

    question = "Which products are likely to run out?"

    print("\nQuestion:")
    print(question)

    print("\nSearching local evidence index...")

    results = retriever.search(
        question,
        top_k=5
    )

    print("\nTop results:\n")

    for result in results:
        print("Document:", result["doc_id"])
        print("Similarity:", result["similarity_score"])
        print("Evidence:", result["text"])
        print("-" * 80)

    print("\nSaved index retrieval test successful!")


if __name__ == "__main__":
    main()