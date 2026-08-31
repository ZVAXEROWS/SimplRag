class RAGPipeline:

    def __init__(
        self,
        loader,
        chunker,
        embedder,
        vector_store,
        generator
    ):

        self.loader = loader
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self.generator = generator

    def index_documents(self):

        documents = self.loader.load()

        all_chunks = []

        for document in documents:

            chunks = self.chunker.chunk(
                document
            )

            all_chunks.extend(chunks)

        texts = [
            chunk.text
            for chunk in all_chunks
        ]

        embeddings = self.embedder.encode(
            texts
        )

        self.vector_store.add(
            all_chunks,
            embeddings
        )

    def ask(self, question, print_top_3 = False):

        query_embedding = self.embedder.encode(
            [question]
        )

        results = self.vector_store.search(
            query_embedding,
            n_results=3
        )

        if(print_top_3 == True):
            self.print_retrieved_chunks(results)

        retrieved_documents = results["documents"][0]

        context = "\n\n".join(
            retrieved_documents
        )

        return self.generator.generate(
            context,
            question
        )

    def print_retrieved_chunks(self, results):

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        print("\n" + "=" * 70)
        print("RETRIEVED CHUNKS")
        print("=" * 70)

        for index, (document, metadata, distance) in enumerate(
            zip(documents, metadatas, distances),
            start=1
        ):

            print(f"\nResult #{index}")
            print(f"Source: {metadata['source']}")
            print(f"Section ID: {metadata['section_id']}")
            print(f"Section Title: {metadata['section_title']}")
            print(f"Chunk ID: {metadata['chunk_id']}")
            print(f"Distance: {distance}")

            print("\nText:")
            print(document)

            print("\n" + "-" * 70)