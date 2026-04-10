# Archive Directory

This directory contains legacy code and exploratory scripts that have been superseded by the modular `src/` library and `experiments/` pipeline.

## `legacy_code/` (formerly `code/`)

**Why archived**: These scripts contained massive code duplication (~500 lines) of functionality already properly implemented in `src/`:
- Duplicate masking strategies (already in `src/attacks/masking.py`)
- Duplicate variant generation (already in `src/models/loader.py`) 
- Duplicate screening logic (already in `src/screening/multi_tool.py`)
- Duplicate metrics calculation (already in `src/analysis/metrics.py`)

**Current approach**: Use `experiments/phase1_gap_test.py` which properly imports from `src/` modules.

**Repository cleanup date**: January 2025
**Reason**: Focus on clean, maintainable codebase for workshop publication timeline

---

These files are preserved for reference but should not be used for active development. The canonical pipeline is:

```bash
# Correct approach:
python experiments/phase1_gap_test.py

# Not this (archived):
python archive/legacy_code/comprehensive_pilot.py  
```