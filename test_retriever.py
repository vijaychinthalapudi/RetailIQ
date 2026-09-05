from src.data_loader import load_all_data
from src.context_builder import build_evidence_documents
from src.embedding_client import embed_documents
from src.retriever import EvidenceRetriever


print("Loading RetailIQ data...")

data = load_all_data()

print("Building evidence documents...")

documents = build_evidence_documents(data)

print("Number of documents:", len(documents))

texts = [
    document["text"]
    for document in documents
]

print("\nCreating embeddings...")

embeddings = embed_documents(texts)

print("Embedding shape:", embeddings.shape)

print("\nCreating retriever...")

retriever = EvidenceRetriever(
    documents,
    embeddings
)

question = "Which products are likely to run out?"

print("\nQuestion:")
print(question)

print("\nRetrieving relevant evidence...")

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