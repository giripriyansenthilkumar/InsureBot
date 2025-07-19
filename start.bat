@echo off
REM Change to script directory
cd /d %~dp0

REM Download sentence-transformers model if not present
if not exist "all-MiniLM-L6-v2" (
    git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
)

REM Create virtual environment if it doesn't exist
if not exist .env (
    python -m venv .env
)

REM Activate the virtual environment
call .env\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

REM (Optional) Test RAG pipeline (uncomment if you want to run rag_brain.py directly)
python rag_brain.py

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Start the Flask app
python app.py

pause