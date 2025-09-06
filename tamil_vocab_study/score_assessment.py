import argparse, csv
from pathlib import Path

def wilson_ci(k, n, z=1.96):
    """Wilson score interval for a binomial proportion (95% by default)."""
    if n == 0: return (0.0, 0.0)
    p = k / n
    denom = 1 + (z*z)/n
    center = (p + (z*z)/(2*n)) / denom
    radius = z * ((p*(1-p)/n + (z*z)/(4*n*n)) ** 0.5) / denom
    return (max(0.0, center - radius), min(1.0, center + radius))

def main():
    ap = argparse.ArgumentParser(description="Score the assessment and estimate vocabulary size")
    ap.add_argument("csv_path", help="Filled assessment CSV")
    ap.add_argument("--external", type=int, default=None, help="Optional external list size L to extrapolate")
    args = ap.parse_args()

    path = Path(args.csv_path)
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    n = len(rows)
    k = sum(1 for r in rows if str(r["passive_known(Y/N)"]).strip().upper().startswith("Y"))
    p = (k / n) if n else 0.0
    lo, hi = wilson_ci(k, n)

    print("===== RESULTS =====")
    print(f"Sample size (n): {n}")
    print(f"Known (passive): {k}/{n} = {p:.3f}")
    print(f"95% CI (Wilson): [{lo:.3f}, {hi:.3f}]")

    # If meta exists, compute in-text vocabulary V̂
    meta = path.with_suffix(".meta.txt")
    if meta.exists():
        T = None
        for line in meta.read_text(encoding="utf-8").splitlines():
            if line.startswith("TOTAL_UNIQUE_TYPES="):
                T = int(line.split("=",1)[1])
        if T is not None:
            V, Vlo, Vhi = round(p*T), round(lo*T), round(hi*T)
            print(f"\nIn-text known vocabulary: {V} (95% CI: {Vlo}–{Vhi}) out of T={T}")

    if args.external is not None:
        Vext, Vext_lo, Vext_hi = round(p*args.external), round(lo*args.external), round(hi*args.external)
        print(f"External list estimate (L={args.external}): {Vext} (95% CI: {Vext_lo}–{Vext_hi})")

if __name__ == "__main__":
    main()
