# Refactor Memo: Dual-Track Split

## Purpose
Split CNG-RTK-HUB into two separate projects for parallel AI agent development:
- **CNG_RTK_HUB_PRO**: Professional RTK client for external hardware
- **CNG_RTK_HUB_EASY**: Enhanced smartphone RTK with direct NTRIP capability

## Risks
- **HIGH**: Project structure changes affect all future development paths
- **MEDIUM**: Divergent codebases may create maintenance overhead
- **LOW**: AI context files may become outdated if not maintained

## Checkpoint Commits
1. `SETUP: Create PRO project structure` - Copy AI context files, validate structure
2. `SETUP: Create EASY project structure` - Enhanced NTRIP foundation ready
3. `VALIDATE: Test Python import stability` - Confirm production backend works
4. `VALIDATE: Test Flutter build process` - APK generation successful
5. `FINALIZE: Update documentation cross-references` - All READMEs aligned
6. `COMPLETE: Dual-track ready for handover` - Tag for AI transition

## Rollback Steps
1. **Immediate**: `git checkout milestone4/enhanced-ntrip` - Return to unified state
2. **Structure**: Delete new project directories, restore original
3. **Tags**: Remove split-related tags, maintain original milestones
4. **Documentation**: Revert to single-project AI context files

## Expected Test Commands
```powershell
# Python backend validation
python -m src.rtk_service

# Flutter build validation
flutter build apk

# Import structure check
python -c "import src.core; print('Imports OK')"

# Git integrity verification
git log --oneline -n 5
```

## Success Criteria
- [ ] Two separate project directories with complete AI context
- [ ] Python backend operational in both projects
- [ ] Flutter builds successful in PRO project
- [ ] Enhanced NTRIP plan ready in EASY project
- [ ] All git branches and tags preserved
- [ ] AI handover documentation complete

## Complexity: **Medium** (4/6 steps)
## Risk Level: **Medium-High** - Architectural change with good documentation

---
*Created: 2025-01-26*
*Branch: refactor/dual-track-split*
*Lead: GitHub Copilot (Refactor-Analyse)*
