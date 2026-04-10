# ProtBreaker: Claude Context File

## Project Overview
**ProtBreaker** evaluates evolutionary constraints in protein language models for biosecurity assessment. Core question: Do evolutionary constraints limit biosecurity risks across protein model architectures?

## Current Status (January 2025)

### Phase 1 Foundation Complete ✅
- **160 variants tested** across ESM-2 650M/3B on 5 toxin proteins
- **0% gap crossing rate**: No variants achieve simultaneous screening evasion + biological function
- **Key findings**: Scaling paradox (3B less plausible than 650M), family-specific patterns
- **Repository**: Clean modular codebase with `experiments/` and `src/` structure

### Workshop Submission Plan (2 weeks) 🔄
- **Target**: NeurIPS 2025 BioSafe Workshop 
- **Focus**: Test evolutionary constraints across ESM-2 → ESM-3 architectures
- **Scope**: 15 proteins × 3 models × 450 variants with ESMfold validation
- **Research question**: "Do evolutionary constraints persist across architectural advances?"

## Technical Environment
- **Local development**: macOS (Claude Code)
- **GPU execution**: When available (H100 access for 35-45 hours needed)
- **Pipeline**: `experiments/phase1_gap_test.py` using modular `src/` library
- **Models**: ESM-2 650M/3B (tested), ESM-3 Medium (planned)

## Key Results
- **Gap persistence**: 0% crossing rate across all conditions tested
- **Scaling paradox**: ESM-2 3B generates less biologically plausible variants than 650M  
- **Family patterns**: Ribosome-inactivating proteins (75-95% evasion) vs neurotoxins (3-40%)
- **Constraint validation**: Structure-function-evasion triangle appears robust

## Repository Structure
```
protbreaker/
├── src/                    # Modular source library
├── experiments/           # Main experimental scripts  
├── data/                  # Protein datasets
├── results/               # Experimental outputs
├── archive/              # Legacy code (archived)
├── plan.md              # Current workshop submission plan
└── CLAUDE.md           # This context file
```

## Next Steps
1. **ESM-3 integration**: Test architectural advance hypothesis
2. **ESMfold validation**: Replace TM-score estimates with real structure prediction
3. **Dataset expansion**: 5 → 15 proteins across 4 families
4. **Workshop paper**: 4-page submission to NeurIPS BioSafe

## Scientific Positioning
- **vs Wittmann et al.**: Explains *why* their demonstrated attacks fail biologically
- **vs Ikonomova et al.**: Tests their constraint hypothesis across AI architectures  
- **Unique contribution**: First cross-architecture biosecurity evaluation with evolutionary explanation

## Research Philosophy
Focus on **evolutionary constraints** as organizing principle rather than attack capability demonstration. Frame as safety validation through biological understanding.

---
*Updated: January 2025*  
*Status: Workshop submission ready, awaiting GPU access*