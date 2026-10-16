"""Score the difficulty-ladder run.
Usage: python scripts/score_ladder.py            -> prints tables, writes results/ladder_summary.json
Needs private/key_L*.csv and private/truth_L*.csv (git-ignored)."""
import csv, json, statistics as st
from collections import defaultdict

LEVELS = ["L0", "L2", "L4"]
MODELS = ["chatgpt", "claude", "gemini"]
P1_CHARS, P2_CHARS = 1023, 1300          # prompt lengths (characters)
CHARS_PER_TOKEN = 4                      # rough English/JSON average
GEMINI_AUDIO_TOK_PER_S = 32              # Gemini API audio tokenisation rate

key, truth = {}, {}
for L in LEVELS:
    for r in csv.DictReader(open(f"private/key_{L}.csv")):
        key[(L, r["track_id"])] = r["label"]
    for r in csv.DictReader(open(f"private/truth_{L}.csv")):
        truth[(L, r["track_id"])] = r

rows = [json.loads(l) for l in open("results/ladder_raw_log.jsonl", encoding="utf-8")]
t1 = {(r["level"], r["model"], r["track_id"]): r for r in rows if r["turn"] == 1}
t2 = [r for r in rows if r["turn"] == 2 and isinstance(r["answer"], dict)]

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

out = {}
for L in LEVELS:
    for m in MODELS:
        items = [r for r in t2 if r["level"] == L and r["model"] == m]
        if not items: continue
        s = defaultdict(int); brier = 0; pairs = []; bases = defaultdict(int); confs = []
        secs, durerr, toks_out, toks_in = [], [], [], []
        for r in items:
            a = r["answer"]; y = key[(L, r["track_id"])] == "ai"; v = a["verdict"].upper() == "AI"
            c = int(a["confidence"]); p = c / 100 if v else 1 - c / 100
            brier += (p - y) ** 2; pairs.append((p, y)); confs.append(c); bases[a.get("main_basis")] += 1
            s["correct"] += (v == y); s["ai_caught"] += (y and v); s["human_called_ai"] += ((not y) and v)
            s["n_ai"] += y; s["n_human"] += (not y); s["said_ai"] += v
            d1 = t1.get((L, m, r["track_id"]))
            if d1:
                a1 = d1["answer"] if isinstance(d1["answer"], dict) else {}
                s["could_not_access"] += a1.get("how_you_accessed_it") == "could not access"
                tr = truth[(L, r["track_id"])]
                if num(a1.get("duration_s")) is not None:
                    durerr.append(abs(num(a1["duration_s"]) - float(tr["duration_s"])))
                s["sr_right"] += str(a1.get("sample_rate_hz")) == tr["sample_rate_hz"]
                s["suno_found"] += (tr["suno_tag"] == "yes" and (a1.get("metadata_suno") is True or "suno" in str(a1.get("metadata_snip", a1.get("embedded_metadata", ""))).lower()))
                if d1["meta"].get("secs") and r["meta"].get("secs"):
                    secs.append(d1["meta"]["secs"] + r["meta"]["secs"])
                # token estimate (visible text only; hidden reasoning, tool I/O not shown, and audio for code models excluded)
                m1, m2 = d1["meta"], r["meta"]
                if m == "chatgpt" and m2.get("pageChars"):
                    vis_out = max(m2["pageChars"] - P1_CHARS - P2_CHARS, 0)
                    o1 = m1.get("pageChars", vis_out // 2) - P1_CHARS
                elif m2.get("allChars"):
                    vis_out = m2["allChars"]; o1 = m1.get("allChars", m1.get("chars", 0))
                else:
                    vis_out = o1 = None
                if vis_out is not None:
                    out_tok = vis_out / CHARS_PER_TOKEN
                    in_tok = (P1_CHARS + (P1_CHARS + o1 + P2_CHARS)) / CHARS_PER_TOKEN
                    if m == "gemini":   # audio is tokenised and sent with both turns
                        in_tok += 2 * GEMINI_AUDIO_TOK_PER_S * float(tr["duration_s"])
                    toks_out.append(out_tok); toks_in.append(in_tok)
        pos = [p for p, y in pairs if y]; neg = [p for p, y in pairs if not y]
        auc = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))
        out[f"{L}_{m}"] = dict(level=L, model=m, n=len(items), **s, brier=round(brier / len(items), 3),
                               auroc=round(auc, 2), conf_min=min(confs), conf_max=max(confs),
                               bases=dict(bases), median_secs=st.median(secs) if secs else None,
                               median_dur_err_s=round(st.median(durerr), 1) if durerr else None,
                               mean_in_tok=round(st.mean(toks_in)) if toks_in else None,
                               mean_out_tok=round(st.mean(toks_out)) if toks_out else None,
                               token_n=len(toks_in))

json.dump(out, open("results/ladder_summary.json", "w"), indent=1)
hdr = "level model   n corr ai_caught hum_as_ai said_ai brier  auroc conf    noaccess med_s  in_tok out_tok"
print(hdr)
for k, d in out.items():
    print(f"{d['level']:5} {d['model']:7} {d['n']:2} {d['correct']:4} {d['ai_caught']:5}/{d['n_ai']} {d['human_called_ai']:6}/{d['n_human']} "
          f"{d['said_ai']:6} {d['brier']:.3f} {d['auroc']:.2f} {d['conf_min']}-{d['conf_max']:<4} {d['could_not_access']:5} "
          f"{str(d['median_secs']):>5} {str(d['mean_in_tok']):>7} {str(d['mean_out_tok']):>6}  {d['bases']}")
