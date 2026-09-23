@echo off
title Buddy Agent (Desktop & Browser Controller)
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" buddy_assistant.py
) else if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" buddy_assistant.py
) else if exist "C:\Users\aditi\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" (
    "C:\Users\aditi\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" buddy_assistant.py
) else (
    python buddy_assistant.py
)
pause
