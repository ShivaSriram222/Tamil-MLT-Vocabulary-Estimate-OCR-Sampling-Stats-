import argparse, csv, random
from pathlib import Path

def load_tokens(tokens_path: str):
    """Read tokens (one per line), dedupe while preserving order."""
    lines = Path(tokens_path).read_text(encoding="utf-8").splitlines()
    seen, out = set(), []
    for w in lines:
        if w and w not in seen:
            seen.add(w); out.append(w)
    return out

def main():
    ap = argparse.ArgumentParser(description="Sample tokens and build an assessment CSV")
    ap.add_argument("tokens", help="Path to mlt_tokens.txt")
    ap.add_argument("out_csv", help="Output assessment CSV")
    ap.add_argument("--n", type=int, default=200, help="Sample size")
    ap.add_argument("--seed", type=int, default=42, help="Random seed (replicability)")
    args = ap.parse_args()

    toks = load_tokens(args.tokens)
    if not toks:
        raise SystemExit("No tokens found. Check OCR step and tokens file.")

    n = min(args.n, len(toks))
    rng = random.Random(args.seed)
    sample = rng.sample(toks, k=n)

    outp = Path(args.out_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["word","passive_known(Y/N)","active_known(Y/N)","definition_or_example","notes"])
        for wd in sample:
            w.writerow([wd,"","","",""])

    # meta (handy for the scorer to compute V̂ = p̂·T)
    outp.with_suffix(".meta.txt").write_text(
        f"TOTAL_UNIQUE_TYPES={len(toks)}\nSAMPLE_SIZE={n}\nSEED={args.seed}\n",
        encoding="utf-8"
    )
    print(f" Wrote assessment CSV with {n} items → {outp}")

if __name__ == "__main__":
    main()
