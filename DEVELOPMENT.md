# Development Setup

## Virtual Environment Setup

**Important**: This project uses a virtual environment to isolate dependencies and prevent conflicts with other Python projects.

### First-time Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Daily Development
```bash
# Always activate the virtual environment first
.\venv\Scripts\Activate.ps1

# Verify you're in the virtual environment (should show (venv) prefix)
# Then run your development commands
python -m src.rtk_service
python -m pytest tests/

# For NTRIP development, test individual components
python -c "import src.core.driver_manager; print('Driver manager ready')"
python -c "import src.api.websocket_server; print('WebSocket API ready')"
```

### Deactivate
```bash
deactivate
```

## Dependency Management

- **Add new dependencies**: Add to `requirements.txt` and run `pip install -r requirements.txt`
- **Virtual environment location**: `venv/` (excluded from git)
- **Python version**: 3.12+ recommended

## IDE Configuration

- **VS Code**: Should auto-detect the virtual environment in `venv/`
- **PyCharm**: Configure interpreter to point to `venv/Scripts/python.exe`

---

**Why virtual environments?**
- Isolates project dependencies from system Python
- Prevents version conflicts between different projects  
- Ensures reproducible development environment
- Required for proper dependency management
