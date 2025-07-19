from sentence_transformers import SentenceTransformer
import faiss
import pickle
import google.generativeai as genai
from openai import OpenAI
from google.api_core.exceptions import ResourceExhausted
import os
import requests

# Load the sentence transformer model for embedding
model = SentenceTransformer('./all-MiniLM-L6-v2')

# Load the FAISS index and document chunks
index = faiss.read_index("model/insura_index.faiss")
with open("model/insura_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# === Configure Gemini ===
genai.configure(api_key="AIzaSyAQYAGbqHXS5FXzPENfzWrVQS5CsWjQY38")

# === Configure OpenRouter ===
openrouter = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # Replace with your actual OpenRouter key
)

AIML_API_KEY = "ecb4f13b9f6440bda3ab2f54c05e7e42"  # Your aimlapi.com key

def get_response(query: str) -> str:
    # Embed the query and retrieve top matching context
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, k=5)
    top_chunks = [chunks[i] for i in I[0]]
    context = "\n".join(top_chunks)

    # Generate response using context
    return generate_reply(query, context)

def generate_reply(query: str, context: str) -> str:
    system_prompt = "You are an insurance expert assistant providing accurate information using only the provided context."
    user_input = f"""
    CONTEXT INFORMATION:
    {context}

    USER QUESTION:
    {query}

    INSTRUCTIONS:
    - Respond using only information from the context.
    - If context doesn't contain answer, state "I couldn't find relevant information."
    - Keep responses professional and factual.
    """

    # === Try Gemini ===
    try:
        model_config = genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=512
        )

        llm = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = llm.generate_content(
            system_prompt + user_input,
            generation_config=model_config
        )
        return response.text.strip()

    except ResourceExhausted:
        print("⚠️ Gemini quota exceeded. Switching to OpenRouter Claude Sonnet...")
    except Exception as e:
        print(f"⚠️ Gemini error: {e}. Switching to OpenRouter Claude Sonnet...")

    # === Try Claude 3 Sonnet via OpenRouter ===
    try:
        response = openrouter.chat.completions.create(
            model="anthropic/claude-3-sonnet-20240229",
            messages=[
                {"role": "system", "content": "You are an insurance expert assistant. Use only the provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
            ],
            max_tokens=1024,
            extra_headers={
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "InsureBot"
            }
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ Claude Sonnet failed or out of credits: {e}. Falling back to cheaper model...")

    # === Fallback: Cheap Model like Mixtral ===
    try:
        response = openrouter.chat.completions.create(
            model="mistralai/mixtral-8x7b",
            messages=[
                {"role": "system", "content": "You are an insurance expert assistant. Use only the provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
            ],
            max_tokens=1024,
            extra_headers={
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "InsureBot"
            }
        )
        return response.choices[0].message.content.strip()

    except Exception:
        pass

    # === Try aimlapi.com using OpenAI client ===
    try:
        client = OpenAI(
            base_url="https://api.aimlapi.com/v1",
            api_key=AIML_API_KEY
        )
        response = client.chat.completions.create(
            model="gpt-4o",  # Or another model supported by aimlapi.com
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        pass

        # === Try RapidAPI Llama as last fallback ===
    try:
        url = "https://open-ai21.p.rapidapi.com/conversationllama"
        headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": "open-ai21.p.rapidapi.com",
            "x-rapidapi-key": "ed49e99973msh594672cd9a67720p17cb1fjsn03c781360344"
        }
        payload = {
            "messages": [
                {"role": "user", "content": query}
            ],
            "web_access": False
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Adjust response parsing as needed
        if "result" in data:
            return data["result"].strip()
        elif "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return str(data)
    except Exception as e:
        return f"❌ All models failed: {str(e)}"