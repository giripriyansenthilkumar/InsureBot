@echo off
REM Create and activate a virtual environment, install requirements, and start Flask app

REM Change to script directory
cd /d %~dp0

REM Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv .env
)

REM Activate the virtual environment
call .env\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Start the Flask app
python app.py

pause