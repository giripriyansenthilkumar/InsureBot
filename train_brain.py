from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

# Ensure model folder exists
os.makedirs("model", exist_ok=True)

# Load the embedding model
model = SentenceTransformer("E:/project/InsureBot/all-MiniLM-L6-v2")

# Load your KB content
with open("kb/policy_knowledge.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Clean + split content into chunks (paragraphs or Q&A)
chunks = [chunk.strip() for chunk in content.split("\n\n") if len(chunk.strip()) > 30]

# Embed all chunks into vectors
embeddings = model.encode(chunks, convert_to_numpy=True)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Save index to disk
faiss.write_index(index, "model/insura_index.faiss")

# Save chunks mapping
with open("model/insura_chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

print(f"✅ Saved {len(chunks)} chunks to 'insura_index.faiss'")
