"""Build docs/data.js (the drill-down data for the results page) from the run logs and the private keys.
Usage: python scripts/build_page_data.py   (needs private/key_*.csv, which are git-ignored)"""
import csv, json, re

# Display names. Human tracks: artist - title (all Creative Commons). AI tracks: generator and style.
NAMES = {
    "h01.mp3": "deeB - Inside the Outside", "h03.mp3": "raja_ffm - the heartstring",
    "h06.mp3": "Mike Chino Beats - Demigods", "h17.mp3": "groucho_marxx - Funky Lagos",
    "h18.mp3": "AFM - Black Strings", "h11.mp3": "Clarence Simpson - Love Is What's Missing",
    "h12.mp3": "Reiswerk - What's your High", "h16.mp3": "Mseq - Miracles",
    "h20.mp3": "AlexBeroza - Man And Machine",
    "f677d052": "Suno v5.5 - lo-fi chillhop", "5b53392d": "Suno v5 - UK garage / house-pop (vocals)",
    "fbcfc643": "Suno v5.5 - jazzy trap", "3b0fa6ea": "Suno v5.5 - afro house",
    "e631a5db": "Suno v5 - dub techno",
    "fake_54122_suno_0": "Suno v3.5 - dance-pop", "fake_53263_udio_1": "Udio - dance",
    "fake_53742_suno_1": "Suno v3.5 - R&B", "fake_53772_suno_0": "Suno v3.5 - electronic pop",
    "fake_53651_udio_1": "Udio - dancehall",
    "fake_52380_suno_0": "Suno v3.5 - dance-pop", "fake_21854_suno_1": "Suno v3.5 - synth dance",
    "fake_05008_suno_0": "Suno v3.5 - R&B pop", "fake_12470_suno_1": "Suno v3.5 - electronic pop",
    "fake_40682_suno_1": "Suno v3.5 - pop-rock",
}
def name(src):
    if src in NAMES: return NAMES[src]
    stem = src.replace(".mp3", "")
    return NAMES.get(stem, NAMES.get(stem[:8], stem))

def keys(path, level=None):
    return {r["track_id"]: r for r in csv.DictReader(open(path))}

K = {L: keys(f"private/key_{L}.csv") for L in ["L0", "L2", "L4", "V", "V2", "F"]}
EXP = {"L0": 1, "L2": 2, "L4": 3, "V": 4, "V2": 5, "F": "F"}

def short(ev):
    t = (ev[0] if ev else "").strip()
    t = re.sub(r"\s*\|\s*", "; ", t).replace(" id <id>", "").replace("<id>", "...")
    return (t[:110] + "...") if len(t) > 110 else t

cells = {}
for log in ["results/ladder_raw_log.jsonl", "results/vocal_raw_log.jsonl",
            "results/vocal_hf_raw_log.jsonl", "results/freq_raw_log.jsonl"]:
    for line in open(log, encoding="utf-8"):
        r = json.loads(line)
        if r["turn"] != 2: continue
        k = K[r["level"]][r["track_id"]]
        a = r["answer"]
        item = dict(track=name(k["source_file"]), truth="AI" if k["label"] == "ai" else "Human",
                    verdict="AI" if a["verdict"] == "AI" else "Human", conf=int(a["confidence"]),
                    why=short(a.get("evidence", [])))
        item["ok"] = item["truth"] == item["verdict"]
        cells.setdefault(f'{EXP[r["level"]]}|{r["model"]}', []).append(item)

# Experiment 5 re-uses Gemini's answers on the 5 human clips from experiment 4 (identical files).
cells["5|gemini"] += [dict(i) for i in cells["4|gemini"] if i["truth"] == "Human"]

for v in cells.values():
    v.sort(key=lambda i: (i["truth"], i["track"]))
summary = {k: dict(correct=sum(i["ok"] for i in v), n=len(v)) for k, v in cells.items()}
open("docs/data.js", "w", encoding="utf-8").write(
    "window.BENCH=" + json.dumps({"cells": cells, "summary": summary}, ensure_ascii=False) + ";\n")
print(json.dumps(summary, indent=0))
