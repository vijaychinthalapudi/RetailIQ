from src.data_loader import load_all_data
from src.context_builder import build_evidence_documents


data = load_all_data()

documents = build_evidence_documents(data)

print("Evidence document generation successful!")
print("Number of documents:", len(documents))

print("\nFirst 5 evidence documents:\n")

for document in documents[:5]:
    print("ID:", document["doc_id"])
    print("Category:", document["category"])
    print("Text:", document["text"])
    print("-" * 80)