# AGGRESSIVE OPTIMIZATION PLAN
**Auto-Delete After Execution** | **Target: 1,200+ Character Reduction** | **Branch: `docs/aggressive-optimization`**

## DEPENDENCY MAP (Critical Dependencies Only)
- `implementation-checklist.md` ← Referenced by all implementation work
- `tech-spec.md` ← Core specification, referenced by checklist
- `architecture-decisions.md` ← ADR template, referenced by 4 files  
- `modular-architecture.md` ← Defines patterns, referenced by checklist + ADRs
- `flutter-python-api.md` ← API contracts, referenced by tech-spec
- `settings-framework.md` ← Profile system, standalone critical component
- Callers: All files cross-reference for implementation guidance

## CANDIDATE CHANGES (File + Lines + Risk + Change Type)

### HIGH-IMPACT CONSOLIDATION
1. **implementation-checklist.md:1-135** | Low Risk | **COMPRESS**
   - Remove: Lines 40-55 (verbose Copilot prompts) → Save ~400 chars
   - Remove: Lines 90-110 (redundant file listings) → Save ~350 chars
   - Compact: Milestone descriptions to single-line → Save ~200 chars

2. **tech-spec.md:1-108** | Low Risk | **EXTRACT+MERGE**
   - Extract: JSON schema (lines 25-45) → Merge into implementation-checklist → Save ~500 chars
   - Remove: Lines 80-108 (security/testing duplicated in ADRs) → Save ~600 chars

3. **architecture-decisions.md:1-136** | Medium Risk | **RESTRUCTURE**
   - Convert: 8 ADRs to compact table format → Save ~800 chars
   - Remove: Verbose consequences (lines 20,35,50,65,80,95,110,125) → Save ~600 chars

### MERGE OPERATIONS
4. **modular-architecture.md:1-108** | Medium Risk | **MERGE**
   - Target: Merge core patterns into implementation-checklist architecture section
   - Remove: Standalone file after merge → Save ~2,400 chars

5. **flutter-python-api.md:1-35** | Low Risk | **INLINE**
   - Target: Inline API table into tech-spec.md
   - Remove: Standalone file → Save ~800 chars

## BRANCH PLAN
**Branch**: `docs/aggressive-optimization`

### Checkpoint Commits
1. **"consolidate: merge flutter-python-api into tech-spec"** 
   - Inline API table, delete standalone file
   - Test: `grep -r "flutter-python-api" .github/notes/` should return 0 results

2. **"compress: reduce implementation-checklist verbosity"**
   - Remove Copilot prompts, compress milestone descriptions
   - Test: `wc -c implementation-checklist.md` should show ~2,800 chars (was ~4,000)

3. **"restructure: convert ADRs to compact table format"**
   - Replace verbose ADR format with condensed decision table
   - Test: `wc -l architecture-decisions.md` should show ~40 lines (was 136)

4. **"merge: integrate modular-architecture into implementation-checklist"**
   - Add architecture patterns section to checklist, delete standalone
   - Test: File count should be 7 (was 9)

5. **"optimize: remove tech-spec redundancies"**
   - Delete security/testing sections duplicated in ADRs
   - Test: `wc -c tech-spec.md` should show ~1,500 chars (was ~2,800)

6. **"validate: final file structure and character counts"**
   - Verify all references, test smoke commands
   - Test: Total character reduction ≥1,200

### Smoke Tests (Windows PowerShell)
```powershell
# After each checkpoint
cd ".github/notes"; Get-ChildItem "*.md" | Measure-Object | Select Count
cd ".github/notes"; Get-ChildItem "*.md" | ForEach { (Get-Content $_.Name | Measure-Object -Character).Characters } | Measure-Object -Sum
grep -r "modular-architecture.md" . | wc -l  # Should be 0 after merge
grep -r "flutter-python-api.md" . | wc -l   # Should be 0 after inline
```

## MEMO TEMPLATE: `.github/notes/docs-aggressive-optimization-memo.md`
```markdown
# Aggressive Documentation Optimization Memo

**Purpose**: Achieve 1,200+ character reduction while maintaining implementation-readiness

**Risk Assessment**: 
- Low: API inlining, verbosity reduction
- Medium: File merging, ADR restructuring
- High: None identified

**Checkpoint Commits**:
1. `feat: inline flutter-python-api → tech-spec`
2. `refactor: compress implementation-checklist verbosity` 
3. `restructure: ADRs to compact table format`
4. `merge: modular-architecture → implementation-checklist`
5. `cleanup: remove tech-spec redundancies`
6. `validate: optimization targets achieved`

**Rollback Steps**:
1. `git checkout main` (return to original state)
2. `git branch -D docs/aggressive-optimization` (delete branch)
3. Alternative: `git revert <commit-hash>` for selective rollback

**Expected Test Commands**:
- Character count validation: `Get-ChildItem "*.md" | ForEach { ... } | Measure-Object -Sum`
- File count verification: `Get-ChildItem "*.md" | Measure-Object | Select Count`
- Reference integrity: `grep -r "deleted-file.md" .`

**Success Criteria**:
- Total character reduction: ≥1,200 characters
- File count reduction: 9 → 7 files  
- All references maintained and functional
- Implementation-readiness preserved
```

## ROLLBACK STEPS (Git Actions)
1. **Safe Rollback**: `git checkout main; git branch -D docs/aggressive-optimization`
2. **Selective Rollback**: `git revert <commit-hash>` for specific checkpoints
3. **Emergency Restore**: `git reflog` to find pre-optimization state
4. **Reference Repair**: Manual fix if cross-references break during merge

## FINAL CHECKLIST (Before Handover to Refactor - Implement)
- [ ] Character reduction ≥1,200 verified via PowerShell measurement
- [ ] File count reduced from 9 → 7 (2 files merged/deleted)
- [ ] All cross-references updated and functional
- [ ] Implementation-checklist.md remains primary entry point
- [ ] tech-spec.md maintains core specification completeness
- [ ] No broken references in any remaining documentation
- [ ] Smoke tests pass: file counts, character counts, grep validations

## COMPLEXITY ESTIMATE
**Size**: Medium (4-6 steps)  
**Risk**: Low-Medium (file merging requires careful reference updates)  
**Duration**: 45-60 minutes for complete execution  
**Character Target**: 1,200-1,500 character reduction (vs previous 600-700)

---
**EXECUTION TRIGGER**: Execute this plan to achieve aggressive optimization goals and resolve character reduction shortfall identified by user analysis.

**AUTO-DELETE**: This file will be removed after successful execution and validation.
