import argparse, re
from pathlib import Path
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import pytesseract

# Unicode range for Tamil letters
TAMIL_BLOCK = r"\u0B80-\u0BFF"

def crop_left_column(img, frac: float):
    """Crop the left 'frac' portion (0.35–0.45 works well for McAlpin)."""
    w, h = img.size
    return img.crop((0, 0, int(w * frac), h))

def preprocess(img, threshold_scale: float = 0.9):
    """Simple grayscale + threshold to help OCR focus on dark text."""
    g = img.convert("L")
    arr = np.array(g)
    thresh = arr.mean() * threshold_scale
    bw = (arr > thresh) * 255
    return Image.fromarray(bw.astype(np.uint8))

def keep_tamil_and_spaces(txt: str) -> str:
    """Remove everything except Tamil letters and whitespace."""
    return re.sub(fr"[^{TAMIL_BLOCK}\s]", " ", txt)

def tokenize_tamil(txt: str):
    """Split on spaces, then filter tokens by length to reduce noise."""
    txt = keep_tamil_and_spaces(txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    toks = [t for t in txt.split(" ") if t]
    return [t for t in toks if 2 <= len(t) <= 20]  # crude noise filter

def main():
    ap = argparse.ArgumentParser(description="OCR left (MLT) column of McAlpin_Tamil.pdf → tokens")
    ap.add_argument("pdf", help="Path to McAlpin_Tamil.pdf")
    ap.add_argument("out_tokens", help="Write unique tokens here (one per line)")
    ap.add_argument("--dpi", type=int, default=350, help="Rasterization DPI (300–400 is good)")
    ap.add_argument("--left-frac", type=float, default=0.40, help="Left column width fraction (0.35–0.45)")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    outp = Path(args.out_tokens)
    outp.parent.mkdir(parents=True, exist_ok=True)

    # 1) PDF → images
    pages = convert_from_path(str(pdf), dpi=args.dpi)
    N = len(pages)

    tokens = set()
    for i, pg in enumerate(pages, 1):
        left_img = crop_left_column(pg, args.left_frac)
        proc = preprocess(left_img, threshold_scale=0.9)
        txt = pytesseract.image_to_string(proc, lang="tam")  # Tamil model
        tokens.update(tokenize_tamil(txt))
        if i % 3 == 0:
            print(f"[{i}/{N}] tokens so far: {len(tokens)}")

    # 2) write unique tokens (sorted, one per line)
    uniq = sorted(tokens)
    outp.write_text("\n".join(uniq), encoding="utf-8")
    print(f"OCR done. Wrote {len(uniq)} unique tokens → {outp}")

if __name__ == "__main__":
    main()
