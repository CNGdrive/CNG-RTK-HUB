# REFACTOR MEMO: Python Package Structure Fix

**Branch:** `fix/python-package-structure`  
**Complexity:** Medium (4/6 steps)  
**Estimated Time:** 2-3 hours  

## Purpose
Fix Python relative import structure that prevents RTK service from running as module and pytest from collecting tests. Convert to absolute imports and proper package structure.

## Root Cause Analysis
- Relative imports (`from ..core`) fail when modules run outside package context
- Python doesn't recognize `src/` as package when running individual files
- pytest collection fails due to "null bytes" error (false positive from relative imports)
- RTK service can't start with `python -m src.rtk_service`

## Risk Assessment
**HIGH RISK:**
- `src/rtk_service.py` - Main service entry point, critical for production

**MEDIUM RISK:**
- All core modules with relative imports - affects entire system functionality  

**LOW RISK:**
- Package structure files - cosmetic/organizational changes

## Checkpoint Commits

### 1. Convert core module imports
**Files:** `src/core/driver_manager.py`, `src/drivers/zedf9p.py`, `src/api/*.py`
**Test:** `python -c "from src.core.driver_manager import DriverManager"`

### 2. Fix RTK service imports  
**Files:** `src/rtk_service.py`
**Test:** `python -c "from src.rtk_service import RTKService"`

### 3. Update package structure
**Files:** `src/__init__.py`, add `src/__main__.py`
**Test:** `python -m src.rtk_service --help`

### 4. Verify test collection
**Files:** Test validation only
**Test:** `python -m pytest tests/ -v`

### 5. Documentation update
**Files:** `README.md`, execution instructions
**Test:** Manual verification of all commands

### 6. Final validation
**Files:** Run production readiness test
**Test:** `python test_production_readiness.py`

## Rollback Steps
1. `git checkout milestone3/ntrip-client-implementation` - Return to working state
2. `git branch -D fix/python-package-structure` - Remove failed branch
3. `git clean -fd` - Remove any untracked files
4. Alternative: Use absolute imports with PYTHONPATH environment variable

## Expected Test Commands
```powershell
# After each checkpoint:
python -c "from src.core.driver_manager import DriverManager; print('✅')"
python -c "from src.rtk_service import RTKService; print('✅')"  
python -m pytest tests/ -v --tb=short
python -m src.rtk_service --help
python test_production_readiness.py
```

## Success Criteria
- [ ] All imports work without relative import errors
- [ ] pytest can collect and run all tests  
- [ ] RTK service starts with `python -m src.rtk_service`
- [ ] Production readiness test shows 9/9 passed
- [ ] No functionality regression in NTRIP implementation

## Handover Notes
Ready for **Refactor - Implement** phase:
- All target files identified with line-specific changes needed
- Import patterns clearly documented (relative → absolute)
- Test validation strategy defined for each checkpoint
- Rollback plan ready if implementation fails
