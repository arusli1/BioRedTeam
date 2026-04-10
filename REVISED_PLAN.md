# ProtBreaker: Revised Plan - The Structure-Function-Evasion Tradeoff

## Executive Summary

**Core Biological Question**: At what sequence divergence do protein variants become non-functional, and do modern protein foundation models generate biologically plausible threats or just structural mimics?

**Key Finding**: ESM-2 650M generates variants with 85%+ screening evasion, but at 9-20% sequence identity - raising critical questions about biological functionality.

**Research Contribution**: First systematic characterization of the structure-function-evasion tradeoff triangle across modern protein foundation models.

## Scientific Motivation & Literature Positioning

### **The Ikonomova Gap (2026)**
Ikonomova et al. demonstrated that **AI-designed proteins can fold correctly but fail functionally**:
- 300 synthetic protein homologs synthesized and assayed
- Structural similarity (TM-score >0.8) did not predict retained activity
- Critical finding: Even single active-site mutations render proteins non-functional

**Our Contribution**: Test whether newer PFMs (ESM-C, ESM-3, DPLM-2) close this structure-function gap or if screening evasion comes at the cost of biological relevance.

### **The Simecek Precedent (NeurIPS BioSafe 2025)**
Simecek showed ESM-3 can reconstruct protein knots at 85% masking - structures requiring precise spatial arrangements. This established that:
- Advanced models can reconstruct complex topologies with minimal sequence information
- Partial sequence disclosure may not meaningfully reduce reconstruction capability
- Our 85% evasion threshold directly validates this finding for ESM-2 650M

### **The EVEREST Constraint (Gurev et al. 2025)**
Protein language models underperform on viral proteins compared to alignment-based models trained on homologous sequences. Since our dataset includes viral toxins, this suggests:
- Model performance may vary significantly by protein family
- Some toxic proteins may be inherently harder to reconstruct than others
- Need family-stratified analysis beyond simple tier groupings

## Core Biological Hypotheses (Testable & Falsifiable)

### **H1: Functional Cliff Hypothesis**
**Prediction**: Screening evasion occurs at sequence identities too low for biological function
- **Test**: Active Site Preservation Score (ASPS) vs evasion rate correlation
- **Expected**: Negative correlation - evading variants lack critical functional residues
- **Biological basis**: Catalytic sites, binding pockets are highly conserved across evolution

### **H2: Architecture-Function Hypothesis** 
**Prediction**: ESM-C models generate more functionally plausible variants than ESM-2 at equivalent evasion rates
- **Test**: ESM-C 300M vs ESM-2 650M at matched parameter counts
- **Expected**: ESM-C maintains higher ASPS at equivalent screening evasion
- **Biological basis**: Better training methodology captures functional constraints

### **H3: Family Specificity Hypothesis**
**Prediction**: Evasion-function tradeoffs vary by protein family (enzymatic vs structural vs binding)
- **Test**: Stratify results by toxin mechanism (ribosome-inactivating vs neurotoxin vs cytotoxin)
- **Expected**: Enzymatic toxins harder to evade while maintaining function (rigid active sites)
- **Biological basis**: Different constraint types (catalytic vs binding vs structural)

### **H4: Masking Regime Hypothesis**
**Prediction**: Functional preservation cliff occurs at 80-85% masking for most proteins
- **Test**: ASPS vs masking rate curves across protein families
- **Expected**: Sharp functional drop at same masking level where evasion emerges
- **Biological basis**: Critical mass of functional residues required for activity

## Experimental Design (Biologically Grounded)

### **Dataset Stratification by Biological Function**

**Enzymatic Toxins** (Rigid functional constraints):
- Ricin A chain (ribosome inactivation - depurination mechanism)
- Diphtheria toxin (ADP-ribosyltransferase - NAD+ binding essential)
- Tetanus/Botox toxins (zinc metalloprotease - catalytic triad critical)

**Binding Toxins** (Flexible interaction surfaces):
- Alpha-latrotoxin (calcium channel binding)
- Conotoxins (ion channel blocking)

**Membrane Toxins** (Structural constraints):
- Melittin (membrane disruption)
- Gramicidin (pore formation)

### **Functional Preservation Metrics (Beyond TM-Score)**

**Active Site Preservation Score (ASPS)**:
```
ASPS = Σ(conserved_functional_residues × importance_weight) / Σ(all_functional_residues × importance_weight)

Where importance_weight = experimental_evidence_score × evolutionary_conservation_score
```

**Functional Site Categories** (from UniProt + literature):
1. **Catalytic residues** (weight: 1.0) - Essential for enzymatic activity
2. **Binding sites** (weight: 0.8) - Substrate/cofactor interaction  
3. **Structural sites** (weight: 0.6) - Disulfide bonds, metal coordination
4. **Allosteric sites** (weight: 0.4) - Regulatory binding positions

### **Biologically Informed Attack Strategies**

**Conservation-Guided Masking** (Realistic attacker strategy):
- Mask only non-conserved positions (BLOSUM62 score <2)
- Preserve catalytic sites, binding pockets automatically
- Tests: Can models reconstruct functional sites from structural context alone?

**Active-Site Avoidance** (Adversarial but biologically aware):
- Mask everything except known functional residues
- Force model to reconstruct "scaffolding" sequence around active sites
- Tests: Minimal information required for functional reconstruction

**Progressive Functional Erosion**:
- Start with full sequence, iteratively mask functional sites by importance
- Track evasion vs function degradation curves
- Tests: Find optimal evasion/function balance

## Screening Pipeline (Biologically Realistic)

### **Multi-Tool Validation** (Real-world screening robustness):
1. **BLASTP** (E-value: 1e-5) - Industry standard protein homology
2. **HMMER** (E-value: 1e-10) - Family-level profile matching  
3. **PSI-BLAST** (3 iterations) - Remote homology detection
4. **DIAMOND** (fast homology) - High-throughput screening simulation

### **Codon-Usage Integration** (DNA synthesis reality):
- Reverse-translate protein variants with species-specific codon usage
- Test commec screening on DNA sequences (not proteins directly)
- Include synonymous codon optimization for evasion enhancement

## Statistical Design (Powered for Biological Discovery)

### **Sample Size Calculation**:
- **Power**: 80% to detect 20% difference in evasion rates
- **Effect size**: Cohen's d = 0.5 (medium biological effect)
- **Multiple comparisons**: Bonferroni correction for model × family × masking combinations
- **Result**: N≥50 variants per condition (current N=300 total across conditions adequate)

### **Primary Endpoints** (Pre-registered):
1. **Structure-Function Correlation**: ASPS vs TM-score correlation by masking rate
2. **Evasion-Function Tradeoff**: ASPS vs evasion rate across models
3. **Architecture Effect**: ESM-C vs ESM-2 functional preservation at matched parameters

### **Family-Wise Error Control**:
- **Primary comparisons**: 5 models × 3 protein families = 15 comparisons
- **Correction**: Benjamini-Hochberg (less conservative than Bonferroni)
- **Alpha**: 0.05 with FDR control at 0.05 level

## Biological Impact & Policy Relevance

### **Threat Assessment Matrix**:

| **Scenario** | **High Evasion** | **High Function** | **Biosecurity Risk** | **Mitigation** |
|--------------|------------------|-------------------|---------------------|----------------|
| Current State | ❌ (0% at <80%) | ✅ (TM>0.8) | LOW | Monitor scaling |
| Functional Cliff | ✅ (85%+) | ❌ (ASPS<0.3) | LOW | Structure-function gap protects |
| Architecture Advance | ✅ (ESM-C) | ✅ (ASPS>0.7) | **HIGH** | Enhanced screening needed |
| Iterative Refinement | ✅ (Multi-round) | ✅ (Gradual degradation) | **HIGH** | Process-based detection |

### **Policy Recommendations by Outcome**:

**If H1 confirmed** (Functional Cliff):
- Current screening adequate for near-term
- Monitor model advances quarterly
- Focus on iterative refinement detection

**If H2 confirmed** (Architecture matters):
- Architecture-specific screening thresholds
- Enhanced monitoring of ESM-C class models
- Industry guidance on model capability assessment

**If H3 confirmed** (Family-specific patterns):
- Toxin-specific screening protocols
- Family-aware E-value thresholds
- Specialized HMM profiles for high-risk families

## Responsible Disclosure Framework

### **Information Hazard Assessment**:

**LOW RISK** (Public release):
- Statistical trends, model comparisons
- Aggregate evasion rates by family
- Defense mechanism effectiveness

**MEDIUM RISK** (Restricted access):
- Specific attack methodologies
- Detailed masking strategies  
- Model-specific optimization techniques

**HIGH RISK** (Controlled access only):
- Raw evading sequences for functional proteins
- Complete attack pipeline code
- Optimization procedures for specific toxins

### **Stakeholder Engagement**:
- **Synthesis companies**: Screening threshold recommendations
- **Model developers**: Capability assessment frameworks
- **Regulatory bodies**: Risk stratification guidelines

## Revised Timeline & Milestones

### **Phase 1: Foundation Validation** (Weeks 1-4)
**Week 1-2**: ESM-C integration + extended masking pipeline
**Week 3-4**: Multi-tool screening + functional annotation integration
**Milestone**: Reproduce 85% evasion finding with functional analysis

### **Phase 2: Systematic Characterization** (Weeks 5-8)  
**Week 5-6**: Complete model matrix (ESM-2, ESM-C across scales)
**Week 7-8**: Family-stratified analysis + statistical testing
**Milestone**: Structure-function-evasion tradeoff characterized

### **Phase 3: Advanced Attacks & Defense** (Weeks 9-12)
**Week 9-10**: Iterative refinement + adversarial optimization  
**Week 11-12**: Defense mechanisms + adaptive attacks
**Milestone**: Complete benchmark with defense evaluation

### **Phase 4: Publication & Disclosure** (Weeks 13-16)
**Week 13-14**: Responsible disclosure review + IRB approval
**Week 15-16**: Paper writing + venue-specific optimization
**Milestone**: NeurIPS main track submission ready

## Success Metrics (Biologically Meaningful)

### **Scientific Success**:
1. **Clear structure-function-evasion tradeoff characterization**
2. **Model capability thresholds for regulatory consideration**
3. **Defense mechanisms with measured effectiveness**
4. **Policy-relevant risk stratification framework**

### **Biological Validity Checks**:
1. **Evading variants maintain minimal functional residues** (ASPS >0.3)
2. **Family-specific patterns match biological constraints**
3. **Results consistent with protein evolution principles**
4. **Generated sequences pass basic biophysical filters** (hydrophobicity, charge, etc.)

## Resource Requirements

### **Compute Budget** (Biologically justified):
- **Functional analysis overhead**: +100 GPU hours (structure prediction for function assessment)
- **ESM-C model evaluation**: +80 GPU hours (architectural comparison)
- **Extended masking ranges**: +60 GPU hours (focus on biologically relevant 80-90%)
- **Multi-tool screening**: +40 GPU hours (comprehensive validation)
- **Total**: 480 GPU hours (vs original 300)

### **Personnel Requirements**:
- **Bioinformatics expertise**: UniProt annotation parsing, functional analysis
- **Structural biology consultation**: TM-score interpretation, functional site identification  
- **Biosecurity expertise**: Threat assessment, responsible disclosure protocols

## Critical Assumptions & Validation

### **Key Assumptions to Test**:
1. **ESM-C models accessible via HuggingFace API** ✓ (confirmed in technical implementation)
2. **UniProt functional annotations complete for toxin proteins** ✓ (manually verified for pilot proteins)
3. **85% evasion threshold generalizes across protein families** ❓ (needs validation)
4. **Structure prediction (ESMfold/AF2) reliable for divergent sequences** ❓ (potential confound)

### **Validation Experiments**:
1. **Cross-family evasion consistency**: Test 85% threshold on all 5 pilot proteins
2. **Functional annotation completeness**: Manual literature review vs UniProt coverage
3. **Structure prediction bias**: ESMfold vs AlphaFold2 correlation at low sequence identity
4. **Screening tool consistency**: BLASTP vs HMMER vs PSI-BLAST agreement rates

This revised plan transforms ProtBreaker from a simple ML benchmark into a comprehensive biological study addressing the fundamental question: **At what point do AI-generated protein variants become biologically irrelevant, and do modern foundation models stay within functional bounds or cross into pure structural mimicry?**

The answer has direct implications for both biosecurity policy and our understanding of protein sequence-structure-function relationships.