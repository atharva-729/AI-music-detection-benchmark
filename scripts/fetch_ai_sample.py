"""Download the 20 sampled Suno v5/v5.5 tracks listed in dataset/ai_sample_manifest.csv into raw/ai/.

Run from the repo root:  python scripts/fetch_ai_sample.py
Uses curl (not Python's ssl) so it behaves like the manual command in HANDOFF.md.
Skips files that already exist, so it is safe to re-run.
"""
import csv, os, subprocess, sys

BASE = 'https://huggingface.co/datasets/Kukedlc/suno-ai-music-dataset/resolve/main/audio/'
os.makedirs('raw/ai', exist_ok=True)
ids = [r['id'] for r in csv.DictReader(open('dataset/ai_sample_manifest.csv', encoding='utf-8'))]
failed = []
for i in ids:
    dst = f'raw/ai/{i}.mp3'
    if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
        continue
    r = subprocess.run(['curl', '-sfL', '-o', dst, f'{BASE}{i}.mp3'])
    ok = r.returncode == 0 and os.path.getsize(dst) > 100_000
    print(('ok   ' if ok else 'FAIL ') + i)
    if not ok:
        failed.append(i)
        if os.path.exists(dst): os.remove(dst)  # don't keep HTML block pages
print(f'{len(ids) - len(failed)}/{len(ids)} present in raw/ai/')
sys.exit(1 if failed else 0)
