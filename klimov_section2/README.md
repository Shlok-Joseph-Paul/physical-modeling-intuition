# Learn Section 2 of Pietryga et al.

Start with these two self-contained lessons. They assume little or no quantum mechanics and require no Python knowledge.

| Lesson | Open and run | What it develops |
| --- | --- | --- |
| **01 · Foundations** | [Open in Colab](https://colab.research.google.com/github/Shlok-Joseph-Paul/physical-modeling-intuition/blob/main/klimov_section2/01_foundations.ipynb) · [Read on GitHub](01_foundations.ipynb) | Probability amplitudes, confinement, effective mass, bands, holes, excitons, and energy bookkeeping |
| **02 · Spherical quantum box (§2.1)** | [Open in Colab](https://colab.research.google.com/github/Shlok-Joseph-Paul/physical-modeling-intuition/blob/main/klimov_section2/02_spherical_quantum_box.ipynb) · [Read on GitHub](02_spherical_quantum_box.ipynb) | Figure 1 and equations (1)–(8), wavefunctions and states, electron/hole energies, Coulomb corrections, and model limits |

## How to study

1. Open Lesson 01, then choose **File → Save a copy in Drive**.
2. Select **Runtime → Run all**; a CPU runtime is sufficient.
3. Read one section, write a prediction, then change its controls.
4. Edit the **My reasoning** text cells to save your explanations. Save the notebook after editing controls or answers.
5. Complete the closed-notes questions before moving to Lesson 02.

Allow two or three sittings of roughly 35–50 minutes for the foundations and two or three for §2.1. These are pacing suggestions, not deadlines. Revisit the transfer questions the next day.

The code is supplied and collapsed in Colab. **Sliders and dropdowns now appear directly in each experiment's form.** They do not depend on saved Jupyter widgets or expandable output panels. Run the cell once; changing a control then reruns it automatically. If a plot does not refresh, press the cell's ▶ button again. Keep the runtime connected. In local Jupyter, the standard live widgets remain visible.

Each lesson runs independently, without loading files from the repository. GitHub displays saved plots but cannot run controls.

**Already saved a Drive copy?** Existing copies do not automatically receive GitHub updates. Reopen the links above and save a new copy, preserving any reasoning you wrote in the old one.

**Expanded Section 3:** The foundations now explain the physical box, the Schrödinger equation and curvature, the sine/cosine solution, both wall conditions, the integer wave numbers, normalization, and the resulting energies. Two new experiments let you test which waves fit and why the normalization factor is needed.

### What “understood” means

Explain the paper's notation and figures, interpret the assumptions behind each equation, predict changes before using the controls, solve a new numerical example, and explain why the model can fail. Matching an answer without explaining it is a reason to revisit the experiment.

## Scope and scientific conventions

These lessons cover foundations and **§2.1 only**. Absorption, multiband holes, fine structure, and lifetimes (§§2.2–2.5) are planned next.

- Source: Pietryga et al., *Spectroscopic and Device Aspects of Nanocrystal Quantum Dots*, Chemical Reviews **116**, 10513–10622 (2016), [DOI: 10.1021/acs.chemrev.6b00169](https://doi.org/10.1021/acs.chemrev.6b00169). §2.1 occupies journal pp. 10515–10517.
- Figures and exercises are newly created model calculations, not experimental data. The copyrighted source PDF is not redistributed.
- The §2.1 defaults are **illustrative CdSe-like parameters**, not a fitted material model: 1.75 eV bulk gap, electron mass 0.13 m₀, hole mass 0.78 m₀, and dielectric constant 6.
- Radius is always in nm; energies are in eV; mass ratios use free-electron mass. SI Coulomb formulas explicitly include 4πε₀.
- Main calculations retain the paper's printed Coulomb coefficient **1.765**. An independently evaluated ground-state integral gives **1.78607317**; the notebook documents this consistency difference instead of silently changing the source.
- Large-radius and very-small-radius sliders explore formal model trends, not certified material accuracy.

## Local use and validation

Python 3.10+ is recommended. Install requirements.txt in your own environment, then open either notebook in Jupyter.

Run the independent checks from the repository root:

    python klimov_section2/validate_lessons.py

To also execute both notebooks in fresh kernels and save a review copy, use:

    python klimov_section2/validate_lessons.py --execute --output-dir /tmp/klimov-lesson-review

Validation covers state normalization and orthogonality, Bessel roots, independent energy calculations, the Coulomb integral, parameter extremes, widget observers, native Colab form inputs and feedback, notebook structure, and fresh-kernel execution. Local execution does not establish compatibility with every institution's Colab browser policy.
