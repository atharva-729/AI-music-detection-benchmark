"""Score the vocal round (V) and frequency test (F). Usage: python scripts/score_vocal.py
Needs private/key_V.csv and private/key_F.csv (git-ignored). Writes results/vocal_summary.json."""
import csv, json
def score(log, keyfile):
    key = {r["track_id"]: r for r in csv.DictReader(open(keyfile))}
    out = {}
    for l in open(log, encoding="utf-8"):
        r = json.loads(l)
        if r["turn"] != 2: continue
        k = key[r["track_id"]]; a = r["answer"]; y = k["label"] == "ai"; v = a["verdict"] == "AI"; c = int(a["confidence"])
        p = c / 100 if v else 1 - c / 100
        out.setdefault(r["model"], []).append(dict(pair=k.get("pair", ""), label=k["label"], source=k["source_file"],
                                                   verdict=a["verdict"], confidence=c, p_ai=p, correct=v == y,
                                                   basis=a.get("main_basis"), evidence=a.get("evidence", [])))
    summ = {}
    for m, rows in out.items():
        pos = [x["p_ai"] for x in rows if x["label"] == "ai"]; neg = [x["p_ai"] for x in rows if x["label"] == "human"]
        auc = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg)) if pos and neg else None
        summ[m] = dict(n=len(rows), correct=sum(x["correct"] for x in rows),
                       brier=round(sum((x["p_ai"] - (x["label"] == "ai")) ** 2 for x in rows) / len(rows), 3),
                       auroc=auc, items=sorted(rows, key=lambda x: (x["pair"], x["label"])))
    return summ
res = {"vocal": score("results/vocal_raw_log.jsonl", "private/key_V.csv"),
       "freq": score("results/freq_raw_log.jsonl", "private/key_F.csv")}
json.dump(res, open("results/vocal_summary.json", "w"), indent=1)
for part, s in res.items():
    for m, d in s.items(): print(part, m, f"{d['correct']}/{d['n']}", "brier", d["brier"], "auroc", d["auroc"])
