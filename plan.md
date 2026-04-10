# ProtBreaker: Evolutionary Constraints in Protein Language Models
**NeurIPS 2025 BioSafe Workshop Submission**

---

## 🎯 Research Question
**"Do evolutionary constraints limit biosecurity risks across protein language model architectures?"**

**Focus**: Instead of asking *whether* models can generate dangerous variants (Wittmann et al. proved this), we ask *why* they fail to simultaneously optimize screening evasion and biological function - and whether this constraint persists as architectures advance.

## 🔬 Central Hypothesis
**Evolutionary Constraint Persistence**: The structure-function-evasion triangle represents a fundamental biological constraint that persists across protein language model architectures (ESM-2 → ESM-3).

**Testable Predictions**:
1. **Gap Persistence**: 0% crossing rate holds across ESM-2 650M, 3B, and ESM-3
2. **Scaling Paradox**: Larger models generate less biologically plausible variants  
3. **Family Specificity**: Protein mechanism drives evasion (ribosome-inactivating > neurotoxins)
4. **Architectural Robustness**: ESM-3 multimodal training doesn't escape constraints

## 🏆 Unique Contributions
1. **Scaling Paradox**: ESM-2 3B less biologically plausible than 650M (counter-intuitive)
2. **Cross-Architecture Test**: First systematic ESM-3 biosecurity evaluation
3. **Family Risk Stratification**: Biological mechanism drives AI behavior patterns
4. **Evolutionary Framework**: Explains *why* attacks fail biologically

## 🔧 Experimental Design

### Models
- **ESM-2 650M**: Baseline (proven working)
- **ESM-2 3B**: Parameter scaling test
- **ESM-3 Medium**: Architectural advance test

### Dataset
**15 proteins** across **4 families** (ribosome-inactivating, neurotoxins, membrane, enzymatic)

### Experimental Matrix
- **450 variants**: 15 proteins × 3 models × 2 masking rates × 5 variants
- **Masking**: 30% (baseline) and 70% (evasion threshold)  
- **Validation**: ESMfold structure prediction + BLASTP screening

## ⚡ 2-Week Timeline
**Week 1**: ESM-3 integration → ESMfold pipeline → Dataset expansion (5→15 proteins)  
**Week 2**: Generate 450 variants → Statistical analysis → Draft workshop paper

**Resources**: 35-45 GPU hours total

## 📊 Expected Outcomes
- **Constraint Persistence** (most likely): ESM-3 shows 0% gap crossing like ESM-2
- **Architectural Breakthrough** (high impact): ESM-3 shows gap crossing capability
- **Partial Progress** (interesting): ESM-3 shows different but constrained patterns

## 🎯 Success Criteria
**Workshop Paper**: Systematic cross-architecture biosecurity evaluation with biological explanation of constraint mechanisms.

**Strategic Positioning**: 
- vs Wittmann et al.: Explain *why* their attacks fail biologically
- vs Ikonomova et al.: Test their constraint hypothesis across AI architectures

---

**Ready for execution when GPU access available.**