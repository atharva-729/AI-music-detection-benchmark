# HANDOFF: dataset-building context (for Claude Code on another machine)

Written 2026-10-11 from a session on the owner's work laptop. Read README.md first for the project. This file records the dataset decisions made since, and what is left to do.

## Why this file exists
The work laptop's network (Netskope) blocks Hugging Face file downloads (the `*.hf.co` CDN). Metadata downloads fine, audio does not (returns an HTML block page, HTTP 403). The owner is continuing on a personal laptop. **Nothing has been downloaded yet.**

## Goal
Build the benchmark dataset (README §3). The dataset is the most important part. The human tracks must *sound AI-like* (hard cases), so the test is not trivially easy. Targets here: ~20 AI tracks now (owner said 20-30 is enough), and matched human tracks from Creative Commons sources.

## Decisions made
- Human side: Creative Commons music is fine (FMA / MTG-Jamendo, ccMixter, Internet Archive netlabels, Musopen). Use only tracks uploaded/released **before 2022** so they cannot be AI. Favour loud, dense, heavily mastered modern productions and genres AI favours (pop, EDM, hip-hop, lo-fi, ambient, cinematic, jazz-leaning electronic). Match the AI side's genre and vocal/instrumental mix. Avoid famous tracks.
- AI side: owner cannot download from Suno free tier. SONICS (2024, Suno v2-v3.5, Udio, ~40 GB, CC BY-NC 4.0) rejected as too old/weak. Chosen source: **Kukedlc/suno-ai-music-dataset** on Hugging Face (CC-BY-4.0, Suno v5/v5.5, May 2026, 857 rows, each MP3 is a separate file so single files can be downloaded). Backup if more generators are wanted (Udio etc.): `ai-music/ai-music-deduplicated` (MIT per card, WebDataset tars ~21 GB each, up to ~Jul 2025, stream a few items instead of downloading whole tars). No open dataset found with ElevenLabs or explicit Suno v4.5.
- Sampling: stratified by genre family x vocal/instrumental, proportional to the pool, N=20, seed 42.

## About the Kukedlc data (findings)
- 857 rows, ~half are duplicate pairs (Suno makes 2 clips per generation). Includes junk (spoken word, JS code pasted into tags, Portuguese lyrics-only rows) and some old versions (v2/v3.5/v4/v4.5).
- Filters applied: status complete, version in {v5, v5.5}, duration >= 90 s, junk removed, de-duplicated -> **304 unique tracks**.
- Only ~140 rows carry the uploader's own genre labels, so genres were assigned by a keyword classifier on tags/prompt (`scripts/ai_sample/1_classify.py`). Labels are approximate.
- Pool is skewed toward jazz/funk, electronic, hip-hop. 65% instrumental. Strict proportional sampling gives 0 rock/world/country tracks.

## The sample (20 tracks)
`dataset/ai_sample_manifest.csv` (columns: id, generator, family, instrumental, duration_s, tags). Genre family counts: jazz_funk 5, hiphop 3, electronic 3, lofi_chill 2, rnb_soul 2, reggae_dub 2, classical_orchestral 1, ambient 1, latin 1. 35% vocal / 65% instrumental. Generator for all: suno-v5 or suno-v5.5.

## NEXT STEPS (do these)
1. `python scripts/fetch_ai_sample.py` -> downloads the 20 MP3s into `raw/ai/` (git-ignored). Needs `curl`. If it fails with TLS errors on Windows, add `--ssl-no-revoke` to the curl call. Equivalent manual URL: `https://huggingface.co/datasets/Kukedlc/suno-ai-music-dataset/resolve/main/audio/<id>.mp3`.
2. **Open question for the owner:** keep strictly proportional sampling, or switch to "at least one track per genre" so rock, world and country are represented? Sparse/dynamic AI tracks (solo piano, ambient) are README "hard cases" and have only 1-2 slots. If the owner wants a change, edit `2_sample.py` (allocation block) and re-run; pipeline in `scripts/ai_sample/`: `python 1_classify.py metadata.csv fam.json` then `python 2_sample.py` (needs Kukedlc's `metadata.csv` from the HF repo in the working dir; `2_sample.py` writes pick.json).
3. Copy `dataset/ai_sample_manifest.csv` to `private/ai_manifest.csv` if desired (private/ is git-ignored; the manifest here is committed only so this machine can fetch the files).
4. Build the human set (~20) from CC sources above, matching genre and vocal ratio, into `raw/human/`.
5. Sanitise: `GENERATOR=suno-v5.5 scripts/sanitize.sh raw/ai ai B` (the key records one generator per run; the manifest shows which tracks are v5 vs v5.5, so run them separately if exact versions matter), `scripts/sanitize.sh raw/human human B`, then `scripts/verify.sh`.
6. Then the protocol in README §5-6.

## Caveats
- Licence: Kukedlc is CC-BY-4.0 (attribution). Suno terms of service may still apply. Use is internal evaluation only.
- The uploader says the tracks were made on a paid Suno plan; that claim is unverified.
- The manifest lists AI track IDs. If this repo becomes public, treat it as part of the answer key.
- Do not upload `private/` or the key anywhere.
