# Missing Person Finder - Windows PowerShell Setup Script

Write-Host "🚀 Setting up Missing Person Finder for local development..." -ForegroundColor Green

# Check if Python 3.8+ is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3.8+ is required but not installed." -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment and install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
.\.venv\Scripts\pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Open VSCode: code missing-person-finder.code-workspace" -ForegroundColor White
    Write-Host "2. Or open the folder in VSCode: code ." -ForegroundColor White
    Write-Host "3. Press F5 or run 'Run Missing Person Finder' from the debug panel" -ForegroundColor White
    Write-Host "4. Open http://127.0.0.1:8000 in your browser" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Available commands:" -ForegroundColor Cyan
    Write-Host "   • Ctrl+Shift+P → 'Tasks: Run Task' → 'Run Server'" -ForegroundColor White
    Write-Host "   • F5 to debug the application" -ForegroundColor White
    Write-Host "   • Ctrl+Shift+P → 'Python: Select Interpreter' (should auto-detect .venv)" -ForegroundColor White
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
}
