# InsureBot

InsureBot is an AI-powered insurance assistant built with Flask, MongoDB, and Retrieval-Augmented Generation (RAG) using state-of-the-art language models. It provides users with accurate insurance information, a chat interface, user authentication, and customizable settings.

---

## Features

- **User Registration & Login:** Secure authentication with hashed passwords.
- **Chatbot Interface:** Ask insurance-related questions and get context-aware answers.
- **Retrieval-Augmented Generation (RAG):** Combines semantic search (FAISS + Sentence Transformers) with LLMs (Gemini, Claude, Mixtral) for accurate, context-based responses.
- **User Settings:** Personalize chat experience and preferences.
- **Chat History:** View previous conversations.
- **Admin & Info Pages:** About, Privacy Policy, Terms of Service.

---

## Project Structure

```
InsureBot/
│
├── app.py                  # Main Flask application (routes, API, session)
├── rag_brain.py            # RAG pipeline: semantic search + LLM response
├── train_brain.py          # Script to build FAISS index from knowledge base
├── requirements.txt        # Python dependencies
├── start.bat               # Windows batch script for setup and running
├── all-MiniLM-L6-v2/       # Local Hugging Face model (cloned at setup)
│
├── model/
│   ├── insura_index.faiss  # FAISS index for semantic search
│   └── insura_chunks.pkl   # Pickled document chunks for retrieval
│
├── kb/
│   └── policy_knowledge.txt # Insurance knowledge base (plain text)
│
├── templates/              # HTML templates for Flask (Jinja2)
│   ├── index.html
│   ├── main_chat_interface.html
│   ├── chat_history.html
│   ├── user_settings.html
│   ├── user_registration.html
│   ├── user_login.html
│   ├── about.html
│   ├── privacy_policy.html
│   └── terms_of_service.html
│
└── static/                 # Static files (CSS, JS, images)
```

---

## How It Works

1. **Setup & Model Download**
   - `start.bat` clones the required SentenceTransformer model (`all-MiniLM-L6-v2`) from Hugging Face if not present.
   - Installs dependencies and sets up a Python virtual environment.

2. **Knowledge Base Indexing**
   - `train_brain.py` reads `kb/policy_knowledge.txt`, splits it into chunks, embeds them, and builds a FAISS index for fast semantic search.

3. **RAG Pipeline**
   - `rag_brain.py` loads the FAISS index and model.
   - When a user asks a question, it finds the most relevant knowledge chunks and sends them, along with the question, to an LLM (Gemini, Claude, or Mixtral) for a grounded, context-aware answer.

4. **Flask Backend**
   - `app.py` handles user registration, login, settings, chat interface, and API endpoints.
   - User data and settings are stored in MongoDB.

5. **Frontend**
   - HTML templates in `templates/` provide the user interface for chat, login, registration, and settings.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Internet connection (for first-time model download)
- MongoDB Atlas account (or update connection string for local MongoDB)

### Setup Steps

1. **Clone the Repository**
   ```sh
   git clone <your-repo-url>
   cd InsureBot
   ```

2. **Prepare the Knowledge Base**
   - Place your insurance knowledge in `kb/policy_knowledge.txt`.

3. **Run the Setup Script**
   ```sh
   start.bat
   ```
   This will:
   - Clone the Hugging Face model if needed.
   - Create a virtual environment and install dependencies.
   - Build the FAISS index (`train_brain.py`).
   - Start the Flask app.

4. **Access the App**
   - Open your browser and go to: [http://localhost:5000](http://localhost:5000)

---

## Configuration

- **MongoDB URI:** Update the connection string in `app.py` if you use a different MongoDB instance.
- **API Keys:** Set your Gemini and OpenRouter API keys in `rag_brain.py`.

---

## Customization

- **Knowledge Base:** Update `kb/policy_knowledge.txt` with your own insurance content.
- **Templates:** Modify HTML files in `templates/` for UI changes.
- **Settings:** Adjust default user settings in `app.py`.

---

## License

This project is for educational and demonstration purposes.

---

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://faiss.ai/)
- [Hugging Face](https://huggingface.co/)
- [Google Gemini](https://ai.google.dev/)