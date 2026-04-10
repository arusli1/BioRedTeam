# ProtBreaker: 2-Week Workshop Submission Plan

**Goal**: Submit solid workshop paper to NeurIPS BioSafe Workshop  
**Timeline**: 14 days  
**Scope**: Expand Phase 1 foundation to workshop-ready publication

---

## Reality Check: Current Position

### ✅ **What We Have (Strengths)**
- **Solid experimental methodology** with 160 variants tested
- **Interesting negative results**: 0% gap crossing across ESM-2 models
- **Family-specific patterns**: Ribosome-inactivating vs neurotoxin differences
- **Scaling paradox**: ESM-2 3B less plausible than 650M
- **Clean, reproducible codebase** ready for expansion

### ❌ **What We're Missing (Gaps)**
- **Scale**: 160 variants vs Wittmann et al's 76,080
- **Model currency**: ESM-2 (2022) vs available ESM-3 (2024) 
- **Screening validation**: BLASTP-only vs real commercial tools
- **Structure prediction**: TM-score estimates vs actual ESMfold
- **Protein diversity**: 5 proteins vs needed 15-20 for robustness

---

## 14-Day Execution Plan

### **Week 1: Core Technical Validation (Days 1-7)**

#### **Days 1-2: ESM-3 Integration** 🎯
**Priority**: Critical test - does gap persistence hold with newest models?

```python
# Add to pipeline:
models = [
    "facebook/esm2_t33_650M_UR50D",     # existing baseline
    "facebook/esm2_t36_3B_UR50D",       # existing scaling
    "EvolutionaryScale/esm3-medium-2024-03",  # newest architecture
]
```

**Success criteria**: ESM-3 results on existing 5 proteins completed
**GPU budget**: ~5-8 hours

#### **Days 3-4: ESMfold Structure Prediction** 🧬
**Priority**: Replace broken TM-score estimates with real predictions

```python
# Replace this broken formula:
# tm_estimate = 0.2 + 0.8 * (identity ** 1.5)

# With real structure prediction:
from transformers import EsmForProteinFolding
esmfold = EsmForProteinFolding.from_pretrained("facebook/esmfold_v1")
```

**Success criteria**: Real TM-scores for all existing variants
**GPU budget**: ~8-10 hours

#### **Days 5-7: Dataset Expansion** 📊
**Priority**: Expand from 5 to 15 proteins for statistical robustness

**Target families** (3-4 proteins each):
- **Ribosome-inactivating**: Ricin, abrin, modeccin
- **Neurotoxins**: Botulinum A, tetanus, α-latrotoxin
- **Cytolytic**: Melittin, gramicidin, streptolysin
- **Enzymatic**: Diphtheria, cholera, pertussis toxin

**Success criteria**: 15 proteins tested across ESM-2 650M/3B/ESM-3
**GPU budget**: ~15-20 hours

### **Week 2: Analysis & Writing (Days 8-14)**

#### **Days 8-10: Statistical Analysis** 📈
- Cross-model comparison (650M → 3B → ESM-3)
- Family-stratified analysis with proper confidence intervals
- Scaling pattern characterization
- Power analysis validation

#### **Days 11-12: Workshop Paper Writing** ✍️
**4-page structure**:
1. **Introduction** (0.8 pages): Evolutionary constraints in protein models
2. **Methods** (1.2 pages): Joint evaluation framework across architectures  
3. **Results** (1.5 pages): Gap persistence, scaling patterns, family differences
4. **Discussion** (0.5 pages): Biological interpretation, policy implications

#### **Days 13-14: Polish & Submit** 🚀
- Internal review and revision
- Figure optimization for workshop format
- Final submission to NeurIPS BioSafe Workshop

---

## GPU Budget Management

**Total available**: ~145 hours remaining
**Workshop plan**: ~35-45 hours
**Buffer**: 100+ hours for main track expansion if workshop leads to acceptance

| Phase | Task | Hours | Running Total |
|-------|------|-------|---------------|
| Week 1 | ESM-3 integration | 8 | 8 |
| Week 1 | ESMfold prediction | 10 | 18 |  
| Week 1 | Dataset expansion | 20 | 38 |
| Week 2 | Analysis & figures | 5 | 43 |
| **Total** | | **43** | |

---

## Workshop Paper Positioning

### **Title**: "Current Protein Language Models Remain Within the Evolutionary Constraint Triangle"

### **Key Message**: 
Even with architectural advances (ESM-2 → ESM-3), protein foundation models cannot simultaneously optimize screening evasion and functional preservation due to fundamental evolutionary constraints.

### **Contributions**:
1. **Systematic evaluation** across protein families and model architectures
2. **Scaling paradox discovery**: Larger models less biologically plausible
3. **Family-specific patterns**: Mechanism-based evasion differences
4. **Methodological framework** for future model assessment

### **Positioning vs Prior Work**:
- **Wittmann et al.**: Demonstrated attack capability at scale → We explain why attacks fail biologically
- **Ikonomova et al.**: Experimental structure-function gap → We test computational gap persistence  
- **Our contribution**: Evolutionary constraint analysis across model generations

---

## Decision Criteria

### **Submit to Workshop if**:
- ✅ ESM-3 shows same gap persistence pattern as ESM-2
- ✅ ESMfold validates functional cliff phenomenon  
- ✅ 15-protein analysis shows robust family patterns
- ✅ Timeline constraints favor quick publication

### **Pivot to Main Track if**:
- ❌ ESM-3 shows gap crossing behavior (would be major finding)
- ❌ Unexpected results require deeper investigation
- ❌ Have bandwidth for 6-8 week intensive expansion

---

## Success Metrics

### **Week 1 Targets**:
- [ ] ESM-3 gap persistence validated on 5 proteins
- [ ] Real TM-scores replace estimates for all variants
- [ ] Dataset expanded to 15 proteins across 4 families
- [ ] Scaling trend (650M → 3B → ESM-3) characterized

### **Week 2 Targets**:
- [ ] Statistical analysis complete with confidence intervals
- [ ] Workshop paper drafted (4 pages)
- [ ] Clear positioning vs Wittmann/Ikonomova established
- [ ] Submission ready for NeurIPS BioSafe Workshop

### **Overall Success**:
Workshop submission that:
- Establishes priority on evolutionary constraint analysis
- Provides solid foundation for future main track paper
- Contributes meaningfully to biosecurity assessment literature
- Opens pathway for expanded research program

---

## Risk Mitigation

### **Technical Risks**:
- **ESMfold memory issues**: Have backup with AlphaFold2 API
- **ESM-3 access problems**: Focus on ESM-C as alternative
- **Dataset expansion bottlenecks**: Prioritize 3 families minimum

### **Timeline Risks**:
- **Week 1 overrun**: Drop dataset expansion to 12 proteins
- **Analysis complexity**: Focus on core gap crossing metrics
- **Writing delays**: Start draft by Day 10 regardless

### **Publication Risks**:
- **Workshop rejection**: High acceptance rate for solid negative results
- **Reviewer concerns**: Address scale limitations upfront
- **Competitive pressure**: Frame as complementary to Wittmann et al.

---

## Post-Workshop Strategy

### **If Accepted**:
- Use workshop publication as foundation for main track expansion
- Apply for additional compute resources based on workshop validation
- Engage with community feedback for research direction

### **If Rejected** (Low probability):
- Submit to alternative workshops (Trustworthy ML, etc.)
- Use as foundation for direct main track submission
- Continue with expanded research program

---

**Bottom Line**: Workshop submission is realistic, achievable goal that establishes priority and creates platform for expanded research program. The 2-week timeline is aggressive but manageable with focused execution.