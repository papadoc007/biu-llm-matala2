@echo off
setlocal DisableDelayedExpansion

cd /d "%~dp0"
title Multi-Agent Translation System Launcher

echo ===============================================
echo   Multi-Agent Translation System - Launcher
echo ===============================================
echo.
echo This launcher will:
echo 1) Ask for environment settings
echo 2) Save them into .env
echo 3) Install dependencies
echo 4) Start the GUI
echo.

set /p OPENAI_API_KEY=Enter OPENAI_API_KEY:
if "%OPENAI_API_KEY%"=="" (
  echo [ERROR] OPENAI_API_KEY is required.
  pause
  exit /b 1
)

set /p OPENAI_CHAT_MODEL=Enter OPENAI_CHAT_MODEL [gpt-4o-mini]:
if "%OPENAI_CHAT_MODEL%"=="" set OPENAI_CHAT_MODEL=gpt-4o-mini

set /p OPENAI_EMBEDDING_MODEL=Enter OPENAI_EMBEDDING_MODEL [text-embedding-3-small]:
if "%OPENAI_EMBEDDING_MODEL%"=="" set OPENAI_EMBEDDING_MODEL=text-embedding-3-small

set /p OPENAI_TRANSCRIPTION_MODEL=Enter OPENAI_TRANSCRIPTION_MODEL [whisper-1]:
if "%OPENAI_TRANSCRIPTION_MODEL%"=="" set OPENAI_TRANSCRIPTION_MODEL=whisper-1

set /p PIPELINE_OUTPUT_DIR=Enter PIPELINE_OUTPUT_DIR [output]:
if "%PIPELINE_OUTPUT_DIR%"=="" set PIPELINE_OUTPUT_DIR=output

python -c "import os; from pathlib import Path; lines=[f'OPENAI_API_KEY=\"{os.environ.get(\"OPENAI_API_KEY\", \"\")}\"', f'OPENAI_CHAT_MODEL=\"{os.environ.get(\"OPENAI_CHAT_MODEL\", \"\")}\"', f'OPENAI_EMBEDDING_MODEL=\"{os.environ.get(\"OPENAI_EMBEDDING_MODEL\", \"\")}\"', f'OPENAI_TRANSCRIPTION_MODEL=\"{os.environ.get(\"OPENAI_TRANSCRIPTION_MODEL\", \"\")}\"', f'PIPELINE_OUTPUT_DIR=\"{os.environ.get(\"PIPELINE_OUTPUT_DIR\", \"\")}\"']; Path('.env').write_text('\n'.join(lines) + '\n', encoding='utf-8')"
if errorlevel 1 (
  echo [ERROR] Failed to write .env file.
  pause
  exit /b 1
)

echo.
echo [OK] .env file updated.

set OPENAI_API_KEY=%OPENAI_API_KEY%
set OPENAI_CHAT_MODEL=%OPENAI_CHAT_MODEL%
set OPENAI_EMBEDDING_MODEL=%OPENAI_EMBEDDING_MODEL%
set OPENAI_TRANSCRIPTION_MODEL=%OPENAI_TRANSCRIPTION_MODEL%
set PIPELINE_OUTPUT_DIR=%PIPELINE_OUTPUT_DIR%

echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install dependencies.
  pause
  exit /b 1
)

echo.
echo Starting GUI...
python -m streamlit run app_gui.py

endlocal
