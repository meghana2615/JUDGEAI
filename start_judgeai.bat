@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found.
  echo Open this folder in VS Code and run: py -3.12 -m venv .venv
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 pause
