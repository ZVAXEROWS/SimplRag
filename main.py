from DocumentLoader import DocumentLoader 
from Chunker import Chunker
from Embedder import Embedder
from VectorStore import VectorStore
from Generator import Generator
from RAGPipeline import RAGPipeline


loader = DocumentLoader("documents")

chunker = Chunker(
    max_chunk_size=1000
)

embedder = Embedder(
    "all-MiniLM-L6-v2"
)

vector_store = VectorStore(
    "knowledge_base"
)

generator = Generator(
    "gemini-3.5-flash"
)


rag = RAGPipeline(
    loader=loader,
    chunker=chunker,
    embedder=embedder,
    vector_store=vector_store,
    generator=generator
)

rag.index_documents()


documents = loader.load()


question = input(
    "Enter your question: "
)

answer = rag.ask(question,True)

print("\nAnswer:")
print(answer)