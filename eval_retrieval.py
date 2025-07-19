import matplotlib.pyplot as plt
from fpdf import FPDF
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import time
from rag_brain import get_response

# Load model and index
model = SentenceTransformer(os.path.join(os.path.dirname(__file__), 'all-MiniLM-L6-v2'))
index = faiss.read_index("model/insura_index.faiss")
with open("model/insura_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# Test cases
test_cases = [
    {"query": "How do I file a claim for car insurance?", "relevant": ["claim", "car insurance"]},
    {"query": "What is a deductible in insurance?", "relevant": ["deductible"]},
    {"query": "How can I update my address in my insurance policy?", "relevant": ["update", "address"]},
    {"query": "What is not covered under travel insurance?", "relevant": ["not covered", "travel insurance"]},
    {"query": "How do I check the status of my insurance claim?", "relevant": ["status", "claim"]},
]

def evaluate_retrieval(test_cases, k=5):
    correct = 0
    times = []
    for case in test_cases:
        start = time.time()
        query_emb = model.encode([case["query"]])
        D, I = index.search(query_emb, k)
        elapsed = time.time() - start
        times.append(elapsed)
        retrieved = [chunks[i].lower() for i in I[0]]
        if any(any(rel in chunk for chunk in retrieved) for rel in case["relevant"]):
            correct += 1
    accuracy = correct / len(test_cases)
    avg_time = sum(times) / len(times)
    return accuracy, avg_time, times

accuracy, avg_time, times = evaluate_retrieval(test_cases)

# Plotting
plt.figure(figsize=(6,4))
plt.bar(range(1, len(times)+1), times)
plt.xlabel('Test Case')
plt.ylabel('Response Time (s)')
plt.title('Response Time per Query')
plt.tight_layout()
plt.savefig('response_times.png')
plt.close()

# Get user query
user_query = input("Enter your insurance-related query: ")

# Get generated answer using RAG pipeline
generated_answer = get_response(user_query)

# PDF Generation
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=14)
pdf.cell(0, 10, "InsureBot Performance Report", ln=True, align='C')
pdf.ln(10)

pdf.set_font("Arial", size=12)
pdf.cell(0, 10, f"Retrieval Accuracy@5: {accuracy*100:.2f}%", ln=True)
pdf.cell(0, 10, f"Average Response Time: {avg_time:.3f} seconds", ln=True)
pdf.ln(5)

pdf.cell(0, 10, "Sample Input/Output:", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 8, f"Sample Query: {user_query}")
pdf.multi_cell(0, 8, f"Generated Answer:\n{generated_answer}")
pdf.ln(5)

pdf.set_font("Arial", size=12)
pdf.cell(0, 10, "How it works:", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 8,
    "1. User submits a query via the chat interface or this script.\n"
    "2. The system embeds the query and retrieves the most relevant knowledge chunks using FAISS.\n"
    "3. The retrieved context is sent to a language model to generate a grounded, accurate answer.\n"
    "4. The answer is returned to the user in real time."
)
pdf.ln(5)

pdf.set_font("Arial", size=12)
pdf.cell(0, 10, "Efficiency Summary:", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 8,
    f"- The system achieves {accuracy*100:.2f}% retrieval accuracy on sample queries.\n"
    f"- Average response time per query is {avg_time:.3f} seconds.\n"
    "- The retrieval process is efficient and suitable for real-time applications."
)
pdf.ln(5)

pdf.set_font("Arial", size=12)
pdf.cell(0, 10, "Response Time Graph:", ln=True)
pdf.image('response_times.png', x=10, w=pdf.w-20)
pdf.ln(10)

pdf.output("InsureBot_Performance_Report.pdf")
print("✅ PDF report generated: InsureBot_Performance_Report.pdf")