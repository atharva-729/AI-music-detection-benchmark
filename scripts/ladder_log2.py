"""Log both turns of one chat. Usage: python scripts/ladder_log2.py <level> <model> <order> <track_id> < captured.txt
stdin: turn-1 capture, a line '=====', turn-2 capture. Each capture = one meta JSON line, then the answer JSON (or text)."""
import json, sys, datetime
lv, model, order, tid = sys.argv[1:5]
blocks = sys.stdin.read().split("\n=====\n")
import os
with open(os.environ.get("LADDER_LOG", "results/ladder_raw_log.jsonl"), "a", encoding="utf-8") as f:
    for turn, b in enumerate(blocks, 1):
        meta_line, _, rest = b.strip().partition("\n")
        try: meta = json.loads(meta_line)
        except Exception: meta, rest = {"raw_meta": meta_line}, rest
        try: ans = json.loads(rest.strip())
        except Exception: ans = rest.strip()
        f.write(json.dumps({"level": lv, "model": model, "order": int(order), "track_id": tid, "turn": turn,
                            "meta": meta, "answer": ans,
                            "logged": datetime.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False) + "\n")
        v = ans.get("verdict") if isinstance(ans, dict) else None
        print(f"logged {lv} {model} #{order} {tid} turn {turn}" + (f" -> {v} {ans.get('confidence')} ({ans.get('main_basis')})" if v else ""))
