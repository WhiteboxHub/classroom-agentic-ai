# Fixing Version Mismatch Issues

## Problem
If you encounter this error:
```
ModuleNotFoundError: No module named 'langchain_core.pydantic_v1'
```

This is a version compatibility issue between LangChain packages.

## Solution

### Option 1: Use the PowerShell Script (Recommended for Windows)
```powershell
cd classroom-customer-service-agentic-google-adk-phase-2-\langraph_agentic
.\install_dependencies.ps1
```

### Option 2: Manual Fix

1. **Uninstall old versions:**
   ```bash
   pip uninstall -y langchain langchain-openai langchain-community langchain-core langgraph
   ```

2. **Install correct versions:**
   ```bash
   pip install -r requirements.txt
   ```

3. **If still having issues, force reinstall:**
   ```bash
   pip install --upgrade --force-reinstall -r requirements.txt
   ```

### Option 3: Install Packages Individually (If above doesn't work)

```bash
pip install langchain-core==0.2.38
pip install langchain==0.2.16
pip install langchain-openai==0.1.23
pip install langchain-community==0.2.16
pip install langgraph==0.2.34
```

## Verified Compatible Versions

The following versions are tested and compatible:
- `langchain-core==0.2.38`
- `langchain==0.2.16`
- `langchain-openai==0.1.23`
- `langchain-community==0.2.16`
- `langgraph==0.2.34`

## After Fixing

Verify the installation:
```python
python -c "import langchain_core; import langchain_openai; print('Success!')"
```

If this runs without errors, you're good to go!

## Still Having Issues?

1. Make sure you're using Python 3.11 or 3.10
2. Try creating a fresh virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Check for conflicting packages: `pip list | grep langchain`

