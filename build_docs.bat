@echo off
REM Build script for Scrapy Item Ingest documentation on Windows

echo 🔧 Setting up documentation build environment...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install documentation requirements
echo 📦 Installing documentation dependencies...
pip install -r docs\requirements.txt

REM Install the project in development mode
pip install -e .

echo 📚 Building documentation...

REM Clean previous builds
if exist "docs\_build" rmdir /s /q "docs\_build"

REM Build HTML documentation
cd docs
make html

echo ✅ Documentation built successfully!
echo 📖 Open docs\_build\html\index.html to view the documentation

REM Optional: Start local server
if "%1"=="--serve" (
    echo 🌐 Starting local documentation server...
    cd _build\html
    python -m http.server 8000
)
