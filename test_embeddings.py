from src.embedding_client import embed_documents, embed_query


documents = [
    "Boat Headphones at Store S001 have 3 units in stock.",
    "USB-C Cable sales increased by 90.41 percent.",
    "JBL Bluetooth Speaker sales decreased by 34.48 percent."
]


print("Creating document embeddings...")

document_embeddings = embed_documents(documents)

print("Document embedding shape:")
print(document_embeddings.shape)

print("\nCreating query embedding...")

query_embedding = embed_query(
    "Which products are running out of stock?"
)

print("Query embedding shape:")
print(query_embedding.shape)

print("\nEmbedding test successful!")