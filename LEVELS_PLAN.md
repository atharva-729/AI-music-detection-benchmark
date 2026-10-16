# Plan: difficulty ladder (run 2)

Drafted 2026-10-16. Status: **design agreed 2026-10-16; L0, L4, L2 approved for the first night.**

Decisions: "remove the cap" = drop the 15 kHz low-pass for both classes (L2); describe and verdict share one chat; first night runs L0 → L4 → L2 (90 chats), L1 and L3 later.

## Why

The pilot ran only the hardest condition (everything scrubbed, 30 s clip) and every model landed at chance. The owner can't tell these tracks apart by ear either. So run 2 starts from the easiest condition, the untouched file, and removes one giveaway per level. That shows where each model's detection breaks, and whether the models were ever reading the file at all.

## The levels (each removes one thing from the one above)

| Level | What the model gets | What still gives it away | How it's built |
|---|---|---|---|
| **L0 Raw** | The original file, renamed to a random ID | Everything: tags (AI files say `made with suno`), cover art, encoder strings, 48 vs 44.1 kHz, bitrate, length, loudness, frequency ceiling | Copy only |
| **L1 No tags** | Tags and cover art stripped, audio frames untouched | Encoder fingerprints, sample rate, bitrate, length, loudness, frequency ceiling | `-map_metadata -1 -c copy`, no re-encode |
| **L2 Same format** | Re-encoded identically (44.1 kHz, 192k, same LAME), **no low-pass** | Length, loudness, frequency ceiling | Level A without the 15 kHz filter |
| **L3 Capped** | L2 plus the 15 kHz low-pass | Length, loudness, intro/outro | Current Level A, at 192k |
| **L4 Clip** | 30 s clip, −16 LUFS, fades (the pilot condition) | Only the sound | Current Level B |

- Same 10 pilot tracks (5 AI, 5 human, style-matched pairs). Nothing new is added.
- A new random ID for each track at each level, with its own key `private/key_L0.csv` … `key_L4.csv`.
- At build time, ffprobe records the true values for each file (length, sample rate, bitrate, tags, loudness, frequency ceiling) in `private/truth_Lx.csv`, so Turn 1 answers can be checked exactly.

## Each chat has two turns

**Turn 1: describe (no mention of AI).** This tests whether the model can perceive the file at all.

```text
Attached is one audio file. Describe it as precisely as you can.
Do not use web search or song-identification tools. You may analyse the file with code if you are able to.
For any field you cannot actually determine, use null. Do not guess.

Answer with ONLY this JSON object:
{
  "how_you_accessed_it": "listened directly" | "code analysis only" | "both" | "could not access",
  "tempo_bpm": <number or null>,
  "key": "<e.g. A minor, or null>",
  "genre": "<or null>",
  "instruments": ["..."],
  "vocals": "yes" | "no" | "unsure",
  "vocal_description": "<language, gender, lyrics heard, or empty>",
  "structure": "<sections with approximate timestamps>",
  "duration_s": <number or null>,
  "sample_rate_hz": <number or null>,
  "bitrate_kbps": <number or null>,
  "channels": <number or null>,
  "codec": "<or null>",
  "embedded_metadata": "<any tags, comments or encoder strings found in the file, quoted exactly, or 'none found'>",
  "loudness_lufs": <number or null>,
  "highest_frequency_khz": <number or null>
}
```

**Turn 2: verdict (same chat).** This is the README prompt with two edits, since the file is no longer guaranteed clean:
- "Base your judgement only on the audio itself" becomes "Base your judgement only on this file: its sound and anything contained in it."
- The sentence "All metadata, tags, filenames and encoder information have been removed…" is deleted.
- One field is added to the JSON: `"main_basis": "embedded metadata" | "technical properties" | "musical content" | "nothing usable"`.

The two turns are kept in one chat on purpose: the question is what the model concludes once it has looked at everything. Note that L4 then differs from the pilot (single-turn), so comparing L4 with pilot condition B shows whether describing first changes the verdict.

## Models and settings

Same as the pilot so results line up: ChatGPT (temporary chat, Unpersonalized, Think off), Gemini 3.8 Flash (temporary chat, Low), Claude Sonnet 5.5 Medium (normal chat, memory off). One run per item, fresh chat per file, order shuffled per model and level. Run through Claude in Chrome, as in the pilot.

## What we expect (written down before running)

- **Gemini has no code tool**, so it can't read tags or headers. If it truly listens, L0 to L4 should look about the same for it. If its Turn 1 musical description is wrong, it isn't hearing the audio either.
- **ChatGPT and Claude can run code.** If they open the file properly, L0 should be near 10/10 (the tag says Suno) and L1 near 10/10 (48 kHz plus Suno's encoder). If they stay at chance on L0, they aren't really inspecting the file.
- The interesting break is between L1, L2 and L3: once the format is equal, do length, loudness or frequency ceiling still help?
- Caution: in this set the human tracks are *louder* than the AI ones. A model that reasons "loud and compressed means AI" will get L2 and L3 backwards.

## Scoring

- **Verdicts:** `score.py` per level (accuracy, Brier, AUROC, human false-positive rate), plus a ladder table of levels × models.
- **Turn 1, technical fields:** checked against `truth_Lx.csv` (duration ±2 s, sample rate exact, bitrate ±10%, metadata found yes/no, `made with suno` quoted yes/no).
- **Turn 1, musical fields:** vocals are checked against the owner's spot-listen (pilot next step 2). Tempo and instruments are compared across models and spot-checked by ear.
- **Grounding:** did the `main_basis` the model gave match what it actually found in Turn 1?

## Volume and order

The full grid is 5 levels × 10 tracks × 3 models = 150 two-turn chats, roughly 8–10 hours through the browser. That's too long for one night, so the run goes in this order:

1. **L0** (all models): the ceiling. Does anyone read the file?
2. **L4** (all models): Turn 1 at the hardest level, i.e. the pilot's step 1.
3. **L2**: the format-equal, uncapped level.
4. **L1, then L3.**

Stop rule: if a model is at chance on L0 *and* its Turn 1 musical description is wrong, skip its L1–L3 verdicts. Easier levels can't help a model that isn't reading the file.

## Files this adds

- `scripts/make_levels.sh`: builds `blind/L0` … `blind/L4` and the keys and truth tables.
- `scripts/score_describe.py`: scores Turn 1.
- `results/ladder_responses.csv`, `results/ladder_raw_log.jsonl`, `results/ladder_report.md`.
