import numpy as np

from src.embedding_client import embed_query


class EvidenceRetriever:
    def __init__(self, documents, embeddings):
        self.documents = documents
        self.embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )

        if len(self.documents) != len(self.embeddings):
            raise ValueError(
                "Number of documents and embeddings must match."
            )

    def search(self, question, top_k=5):
        """
        Retrieve the most relevant evidence documents
        for a manager's question.

        Document embeddings are loaded from the local
        precomputed index. Only the manager's question
        needs a Gemini embedding at query time.
        """

        if not self.documents:
            return []

        query_embedding = embed_query(question)

        # Both document and query embeddings are normalized,
        # so dot product is equivalent to cosine similarity.
        scores = self.embeddings @ query_embedding

        top_k = min(
            top_k,
            len(self.documents)
        )

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            document = dict(
                self.documents[index]
            )

            document["similarity_score"] = round(
                float(scores[index]),
                4
            )

            results.append(document)

        return results