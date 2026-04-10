# ProtBreaker: Protein Foundation Model Biosecurity Benchmark

A systematic benchmark for evaluating whether protein foundation models can generate variants that simultaneously evade biosecurity screening while maintaining biological function.

## 🎯 Core Research Question

**Have protein foundation models advanced from the Ikonomova limitation (structure OR function) to simultaneous capability (structure AND function AND evasion)?**

## 📊 Key Findings (Phase 1 Foundation)

- **ESM-2 650M/3B**: 0% gap crossing rate across 160 variants (5 proteins)
- **Scaling Paradox**: Larger models generate less biologically plausible sequences  
- **Family Patterns**: Ribosome-inactivating proteins more evasive than neurotoxins
- **Current Status**: Workshop paper ready, main track expansion needed

## 🚧 Current Scope & Limitations

**What's been tested**: 5 toxin proteins, ESM-2 models (650M/3B), BLASTP screening  
**Scale limitation**: 160 variants vs 76,080 in Wittmann et al. (Science 2025)  
**Model currency**: ESM-2 (2022) - needs ESM-3, ESM-C testing  
**Screening gaps**: BLASTP-only vs real commercial synthesis screening tools

## 🏗️ Repository Structure

```
protbreaker/
├── src/                    # Core source code
│   ├── models/            # Model loading and inference
│   ├── attacks/           # Variant generation strategies  
│   ├── screening/         # Multi-tool screening pipeline
│   ├── analysis/          # Results analysis and metrics
│   └── utils/             # Shared utilities
├── data/                  # Datasets and annotations
│   ├── proteins.json      # Pilot protein sequences
│   └── annotations/       # Functional annotations
├── experiments/           # Experimental scripts
│   └── phase1_gap_test.py # Main Ikonomova gap test
├── results/              # Experimental results
├── docs/                 # Documentation
├── configs/              # Configuration files
└── tests/                # Unit tests
```

## 🚀 Quick Start

### Phase 1: Ikonomova Gap Test
```bash
# Test if models cross structure + function + evasion threshold
python experiments/phase1_gap_test.py --model esm2_650m

# Analyze results
python src/analysis/threshold_analysis.py
```

### Key Metrics
- **Gap Crossing Rate**: Variants achieving evasion + structure + function
- **ASPS**: Active Site Preservation Score (functional preservation)
- **TM-Score**: Structural similarity (≥0.5 = same fold)
- **Evasion**: Joint screening evasion (BLASTP + strict thresholds)

## 📈 Experimental Status

### ✅ Phase 1: Foundation (Complete)
- [x] ESM-2 650M/3B baseline assessment (5 proteins)
- [x] Gap crossing analysis framework
- [x] BLASTP screening validation  
- [x] Family-specific pattern identification

### 🚧 Current Phase: Workshop Preparation (2 weeks)
- [ ] ESM-3 and ESM-C integration
- [ ] ESMfold structure prediction validation
- [ ] Expand to 15 proteins across 3-4 families
- [ ] Workshop paper submission

### 📋 Future Phases (Post-Workshop)
- **Main Track Expansion**: 30+ proteins, commec screening, defense mechanisms
- **Advanced Models**: ESM-3, DPLM-2, ProtGPT2 comprehensive testing
- **Theoretical Framework**: Evolutionary constraint analysis

## 🛡️ Responsible Disclosure

This research follows responsible disclosure principles:
- **Public**: Statistical trends, model comparisons
- **Restricted**: Detailed methodologies, attack strategies
- **Controlled**: Raw evading sequences, optimization procedures

## 📚 Key References

- **Ikonomova et al. (2026)**: Structure ≠ Function gap in AI protein design
- **Simecek (NeurIPS BioSafe 2025)**: ESM-3 reconstruction at 85% masking
- **Wittmann et al.**: DNA synthesis screening robustness

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## 📄 License

See [LICENSE](LICENSE) for licensing information.

---

**Note**: This repository contains research tools for biosecurity assessment. Use responsibly and in accordance with institutional guidelines.