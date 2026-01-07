# PowerShell script to install/update dependencies
# This script will uninstall conflicting packages and reinstall with correct versions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fixing LangChain Version Conflicts" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Uninstalling old LangChain packages..." -ForegroundColor Yellow

# Uninstall old versions (suppress errors if not installed)
pip uninstall -y langchain langchain-openai langchain-community langchain-core langgraph chromadb 2>$null

Write-Host ""
Write-Host "Step 2: Installing compatible versions from requirements.txt..." -ForegroundColor Green

# Install from requirements.txt
pip install -r requirements.txt

Write-Host ""
Write-Host "Step 3: Verifying installation..." -ForegroundColor Green

# Check if installation was successful
python -c "import langchain_core; import langchain_openai; print('✓ LangChain packages installed successfully')" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Installation complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "If you still see errors, try:" -ForegroundColor Yellow
    Write-Host "  pip install --upgrade --force-reinstall -r requirements.txt" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or install packages individually:" -ForegroundColor Yellow
    Write-Host "  pip install langchain-core==0.2.38" -ForegroundColor Cyan
    Write-Host "  pip install langchain==0.2.16" -ForegroundColor Cyan
    Write-Host "  pip install langchain-openai==0.1.23" -ForegroundColor Cyan
    Write-Host "  pip install langchain-community==0.2.16" -ForegroundColor Cyan
    Write-Host "  pip install langgraph==0.2.34" -ForegroundColor Cyan
}

