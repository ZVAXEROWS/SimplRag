import chromadb


class VectorStore:

    def __init__(self, collection_name):
        self.client = chromadb.Client()

        self.collection = (
            self.client.create_collection(
                name=collection_name
            )
        )

    def add(self, chunks, embeddings):

        self.collection.add(
            ids=[
                str(i)
                for i in range(len(chunks))
            ],

            documents=[
                chunk.text
                for chunk in chunks
            ],

            embeddings=embeddings.tolist(),

            metadatas=[
                {
                    "source": chunk.source,
                    "section_id": chunk.section_id,
                    "section_title": chunk.section_title,
                    "chunk_id": chunk.chunk_id
                }
                for chunk in chunks
            ]
        )

    def search(self, query_embedding, n_results=3):

        return self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )