# Ma Theory: Optimization-Induced Dynamics and the Inverted-U

**A Distillation-Based Theory of Optimal Misalignment**

*Ma Theory*, from the concept of *ma* ('in-between'), proposes that perfect agreement between cognitive systems is not optimal. Instead, emergence is maximized at an optimal degree of structural divergence (ε*).

## Key Findings

- **Inverted-U relationship**: Emergent utility peaks at ε* ≈ 68 (Pythia-410m) and ε* ≈ 35 (Pythia-160m), not at ε* = 0
- **Process dependence**: The inverted-U appears only under SGD-driven distillation, not under linear weight interpolation
- **Mechanism**: Early saturation of representational novelty (D_nov) is the key enabling condition
- **Replicated** across two model scales under identical experimental conditions

## Repository Structure

```
ma-theory/
├── paper/
│   ├── ma_theory_paper_final.pdf    # Published paper
│   └── ma_theory_paper_final.tex    # LaTeX source
├── experiments/
│   ├── pythia410m_distillation.py   # 410m distillation track code
│   ├── pythia160m_colab.py          # 160m distillation track (Colab)
│   └── interpolation_track.py       # Weight interpolation experiments
├── data/
│   ├── results_410m/                # Raw results (3 seeds)
│   └── results_160m/                # Raw results (3 seeds)
├── figures/
│   ├── fig1_410m_eagree.pdf
│   ├── fig2_160m_eagree.pdf
│   ├── fig3_interp_eagree.pdf
│   └── fig4_dnov_comparison.pdf
└── README.md
```

## Reproducing the Results

All experiments use EleutherAI/Pythia models with publicly available checkpoints on HuggingFace.

### Requirements
- Python 3.10+
- PyTorch 2.0+
- transformers
- peft (for LoRA experiments)
- datasets (WikiText-2)

### Running the distillation track (410m)
```bash
python experiments/pythia410m_distillation.py --seed 42
python experiments/pythia410m_distillation.py --seed 123
python experiments/pythia410m_distillation.py --seed 456
```

### Running the distillation track (160m, Google Colab)
Upload `experiments/pythia160m_colab.py` to Google Colab with A100 GPU runtime.

## Citation

If you use this work, please cite:

```bibtex
@misc{sai2026matheory,
  author = {SAI},
  title = {Optimization-Induced Dynamics and the Inverted-U: A Distillation-Based Theory of Optimal Misalignment},
  year = {2026},
  doi = {10.5281/zenodo.19439785},
  url = {https://doi.org/10.5281/zenodo.19439785}
}
```

## Collaborative Development

This work was developed through a collaborative cognitive framework between a human researcher and multiple large language model agents (Claude by Anthropic, GPT by OpenAI, and Gemini by Google). The author name SAI represents this collaborative entity.

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
