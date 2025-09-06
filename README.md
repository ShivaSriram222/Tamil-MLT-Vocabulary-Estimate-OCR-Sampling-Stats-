# Tamil MLT Vocabulary Estimate (OCR → Sampling → Stats)

**Goal.** Estimate how many **Modern Literary Tamil (MLT)** words I know from the *McAlpin Tamil* PDF, using OCR + random sampling + a 95% Wilson confidence interval.

**Headline result (example numbers from my run):**
- Unique surface forms extracted: **T = 2,600**
- Sampled: **N = 200**, Known: **K = 76** → **p̂ = 0.380**
- 95% CI (Wilson) for p̂: **[0.316, 0.449]**
- Count known **within this list**: **V̂ = p̂ × T = 988** (95% CI **821–1,167**)

> This estimate is **only** for the measured list. I do not extrapolate to “all Tamil.”


## Method (short)
1. **OCR** the PDF (left column only = MLT): Tesseract `lang=tam`, `--psm 6`, `--oem 1`, 350–400 DPI, grayscale + light threshold.
2. **Normalize & filter** Unicode: NFC; strip ZWJ/ZWNJ; keep Tamil block (U+0B80–U+0BFF + spaces); drop Tamil digits (௦–௯); drop virama-only or trailing-virama fragments; length 2–20; **dedupe** → **T** types.
3. **Sample** **N=200** words uniformly at random (seed=42) and label **Y/N** for “passive known” (I can explain in Tamil and use in a short phrase).
4. **Score**: p̂ = K/N; **Wilson 95% CI** for p̂; counts for this list via **V̂ = p̂ × T** (CI bounds × T).



## Reproducible run

### Install (macOS)
- **Tesseract** + Tamil: `brew install tesseract` and `brew install tesseract-lang` (or add `tam.traineddata` manually)
- **Poppler** (for pdf2image): `brew install poppler`
- Python deps: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

### Commands
```bash
# 1) OCR extract → tokens
python scripts/extract_mlt_ocr.py data/McAlpin_Tamil.pdf data/out/mlt_tokens.txt --dpi 400 --left-frac 0.40 --psm 6 --oem 1

# 2) Clean Unicode noise (digits/virama-only/etc.)
python scripts/postfilter_tokens.py data/out/mlt_tokens.txt data/out/mlt_tokens_clean.txt

# 3) Build assessment sheet (random sample)
python scripts/make_assessment_from_tokens.py data/out/mlt_tokens_clean.txt data/out/assessment_mlt.csv --n 200 --seed 42

# 4) Manually label assessment_mlt.csv (Y/N + tiny Tamil phrase),
#    then compute stats & save a small figure
python scripts/score_assessment.py data/out/assessment_mlt.csv
python scripts/plot_results.py data/out/assessment_mlt.csv results/p_hat_ci.png
