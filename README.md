# ProtBreaker: Protein Foundation Model Biosecurity Benchmark

A systematic benchmark for evaluating whether protein foundation models can generate variants that simultaneously evade biosecurity screening while maintaining biological function.

## 🎯 Core Research Question

**Have protein foundation models advanced from the Ikonomova limitation (structure OR function) to simultaneous capability (structure AND function AND evasion)?**

## 📊 Key Findings (Phase 1 Complete)

- **ESM-2 650M**: 0% gap crossing rate (76% evasive, 0% structural, 2% functional)
- **Threshold Status**: SAFE - Models remain within Ikonomova gap
- **Policy Recommendation**: Continue monitoring, maintain current screening protocols

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

### ✅ Phase 1: Stress-Test (Complete)
- [x] ESM-2 650M baseline assessment
- [x] Ikonomova gap threshold analysis
- [x] Multi-tool screening validation
- [x] Functional preservation scoring

### 📋 Next Phases
- **Phase 2**: Defense mechanisms (if threshold crossed)
- **Phase 3**: Advanced model testing (ESM-3, DPLM-2)
- **Phase 4**: Full dataset scaling (740 proteins)

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