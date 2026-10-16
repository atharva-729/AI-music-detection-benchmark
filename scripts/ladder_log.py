"""Append one turn to results/ladder_raw_log.jsonl.
Usage: python scripts/ladder_log.py <level> <model> <order> <track_id> <turn> <meta_json> <answer_file>"""
import json, sys, datetime
lv, model, order, tid, turn, meta, ans = sys.argv[1:8]
raw = open(ans, encoding="utf-8").read().strip()
try:
    answer = json.loads(raw)
except Exception:
    answer = raw
rec = {"level": lv, "model": model, "order": int(order), "track_id": tid, "turn": int(turn),
       "meta": json.loads(meta), "answer": answer, "logged": datetime.datetime.now().isoformat(timespec="seconds")}
with open("results/ladder_raw_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("logged", lv, model, order, tid, "turn", turn)
