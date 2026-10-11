from google import genai
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = []

def chunk_text(text,chunk_size=500,overlap=100):
    chunks =[]

    start =0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap
    return chunks


for file in Path("documents").glob("*.txt"):
    text = file.read_text(encoding="utf-8")

    chunks = chunk_text(text)

    for i,chunk in enumerate(chunks):
        documents.append({
            "text":chunk,
            "source":file.name,
            "chunk_id":i
        })    


texts = [doc["text"] for doc in documents]

embeddings = model.encode(texts)

DBClient = chromadb.Client()

collections = DBClient.create_collection(
    name= "knowledge_Base"
)

collections.add(
    ids=[str(i) for i in range(len(documents))],
    documents=texts,
    embeddings=embeddings.tolist(),
    metadatas=[
        {
            "source" : doc["source"],
            "chunk_id" : doc["chunk_id"]
        }
        for doc in documents
    ]
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

query = input("Enter your prompt: ")

queryEmbedding = model.encode([query]).tolist()

result = collections.query(query_embeddings=queryEmbedding,n_results=3)

retrieved_Documents = result["metadatas"][0]

expanded_documents = []
added_chunks = set()

for metadata in retrieved_Documents:

    source = metadata["source"]
    chunk_id = metadata["chunk_id"]

    for doc in documents :
        if(doc["source"] == source and abs(doc["chunk_id"] - chunk_id ) <=2):
            if (source, doc["chunk_id"]) not in added_chunks:
                expanded_documents.append(doc)
                added_chunks.add((source,doc["chunk_id"]))

# print(expanded_documents)

context = "\n\n".join(doc["text"] for doc in expanded_documents)

prompt = f"""
Answer the question using only the provided context.

context:
{context}

Question:
{query}
"""

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)

print(f"\n\n\n{prompt}\n\n\n")

print("\nAnswer:")
print(response.text)