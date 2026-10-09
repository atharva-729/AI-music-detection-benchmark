#!/usr/bin/env python3
"""Score LLM answers against the private key.

Usage: python3 scripts/score.py private/key.csv results/responses.csv

responses.csv columns:
  model, run, track_id, verdict (AI|HUMAN|ABSTAIN), confidence (50-100), identified_track (yes|no)
"""
import csv, sys, math, random
from collections import defaultdict

key = {r["track_id"]: r["label"].strip().lower() for r in csv.DictReader(open(sys.argv[1]))}
rows = list(csv.DictReader(open(sys.argv[2])))

def p_ai(r):
    """Turn verdict + confidence into P(AI). Abstain / missing -> 0.5."""
    v = r["verdict"].strip().upper()
    if v not in ("AI", "HUMAN"): return 0.5
    c = min(max(float(r["confidence"]) / 100, 0.5), 1.0)
    return c if v == "AI" else 1 - c

def auroc(y, p):
    pos = [q for t, q in zip(y, p) if t]; neg = [q for t, q in zip(y, p) if not t]
    if not pos or not neg: return float("nan")
    return sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))

def ece(y, p, bins=5):
    conf = [max(q, 1 - q) for q in p]; corr = [(q >= 0.5) == t for t, q in zip(y, p)]
    tot = 0
    for b in range(bins):
        lo, hi = 0.5 + b * 0.5 / bins, 0.5 + (b + 1) * 0.5 / bins
        idx = [i for i, c in enumerate(conf) if lo <= c < hi or (b == bins - 1 and c == 1.0)]
        if idx: tot += len(idx) / len(p) * abs(sum(conf[i] for i in idx) / len(idx) - sum(corr[i] for i in idx) / len(idx))
    return tot

def metrics(rs):
    rs = [r for r in rs if r["track_id"] in key]
    y = [key[r["track_id"]] == "ai" for r in rs]; p = [p_ai(r) for r in rs]
    answered = [r["verdict"].strip().upper() in ("AI", "HUMAN") for r in rs]
    pred = [q > 0.5 for q in p]
    tp = sum(a and b for a, b in zip(pred, y)); tn = sum((not a) and (not b) and ans for a, b, ans in zip(pred, y, answered))
    fp = sum(a and not b for a, b in zip(pred, y))
    n_ai = sum(y); n_h = len(y) - n_ai
    tpr = tp / n_ai if n_ai else float("nan"); tnr = tn / n_h if n_h else float("nan")
    brier = sum((q - t) ** 2 for q, t in zip(p, y)) / len(y)
    ll = -sum(math.log(min(max(q if t else 1 - q, 0.01), 0.99)) for q, t in zip(p, y)) / len(y)
    return dict(n=len(y), acc=sum((q > 0.5) == t and a for q, t, a in zip(p, y, answered)) / len(y),
                bal_acc=(tpr + tnr) / 2, ai_recall=tpr, human_fpr=fp / n_h if n_h else float("nan"),
                brier=brier, logloss=ll, auroc=auroc(y, p), ece=ece(y, p),
                abstain=1 - sum(answered) / len(y),
                identified=sum(r.get("identified_track", "no").strip().lower() == "yes" for r in rs) / len(y))

def bootstrap_ci(rs, stat="brier", n=2000, seed=0):
    rnd = random.Random(seed); tracks = sorted({r["track_id"] for r in rs})
    by = defaultdict(list); [by[r["track_id"]].append(r) for r in rs]
    vals = []
    for _ in range(n):
        s = [r for t in (rnd.choice(tracks) for _ in tracks) for r in by[t]]
        if len({key[r["track_id"]] for r in s}) == 2: vals.append(metrics(s)[stat])
    vals.sort(); return vals[int(.025 * len(vals))], vals[int(.975 * len(vals))]

def consistency(rs):
    by = defaultdict(set)
    for r in rs: by[r["track_id"]].add(r["verdict"].strip().upper())
    return sum(len(v) == 1 for v in by.values()) / len(by)

models = defaultdict(list)
for r in rows: models[r["model"]].append(r)
cols = ["n", "acc", "bal_acc", "ai_recall", "human_fpr", "brier", "logloss", "auroc", "ece", "abstain", "identified"]
print(f"{'model':<22}" + "".join(f"{c:>10}" for c in cols) + f"{'consist':>9}{'brier 95% CI':>18}")
for m, rs in sorted(models.items(), key=lambda kv: metrics(kv[1])["brier"]):
    mt = metrics(rs); lo, hi = bootstrap_ci(rs)
    print(f"{m:<22}" + "".join(f"{mt[c]:>10.3f}" if c != "n" else f"{mt[c]:>10d}" for c in cols)
          + f"{consistency(rs):>9.2f}{f'[{lo:.3f}, {hi:.3f}]':>18}")
print("\nReference: always-50% guesser -> brier 0.250, logloss 0.693, auroc 0.500")
