# Can LLMs Hear the Machine?
### A blind benchmark for AI-generated music detection by multimodal LLMs

> Innovation-team project · Owner: Atharva · Status: **run 2 complete (difficulty ladder, 10 tracks, 3 models)**
>
> **Results page: <https://atharva-729.github.io/AI-music-detection-benchmark/>**

---

## 1. What this is about

AI music generators (Suno, Udio and others) now produce tracks most people can't tell apart from human-made music. Streaming platforms are starting to tag AI tracks. Deezer, for example, runs its own detector. Publishers and content platforms need to know whether the audio they host or license is synthetic.

Meanwhile, general-purpose multimodal LLMs (Claude, GPT, Gemini, …) accept audio uploads, and people already ask them *"is this song AI?"*. **Nobody knows how good their answers are, or whether their stated confidence means anything.**

This project builds a small, controlled, **blind** benchmark that answers three questions:

1. **Can off-the-shelf LLMs tell AI-generated music from human-made music**, once every non-audio giveaway (tags, encoder fingerprints, filenames, bitrate) is removed?
2. **Is their confidence calibrated?** When a model says "90% sure", is it right about 90% of the time?
3. **What do they rely on?** Real audio evidence, or shortcuts such as recognising a famous song or guessing from production style?

### Why the "blind" part matters (lessons from the pilot)

In the first informal test, the model got the right answer on one track **without analysing the audio at all**. The ID3 tags named the album, artist and year (2022, which predates usable AI music generators). After the tags were stripped, the file still leaked information:

| Leak | Example from the pilot | Fixed by |
|---|---|---|
| ID3 / container tags | `album: Tomorrow (OST)`, `date: 2022` | `-map_metadata -1` |
| Encoder version inside the audio frames | `LAME3.99.5` (≈2012 encoder) vs `LAME3.100` | Re-encoding every file with the same encoder |
| Bitrate / encoding mode | 128 kbps VBR (a yt-dlp rip) vs 320 kbps CBR | Fixed 192 kbps CBR |
| High-frequency cutoff | 16 kHz vs ~15.5 kHz, set by the source encode | Same low-pass filter on every file |
| Duration | 89 s vs 109 s | Fixed-length clip (Level B) |
| Loudness / dynamics | AI clip loud and compressed, human clip very dynamic | Loudness normalisation (Level B) |
| Filename | `out.mp3`, `Opening_Title.mp3` | Random IDs |
| Track recognition | Famous songs can be identified, not detected | Prefer obscure tracks + ask the model to disclose |

Note that `ffmpeg -c copy` **does not** remove encoder fingerprints. It copies the audio frames unchanged, and the `LAME x.y.z` string inside them survives. The only fix is to decode and re-encode everything identically.

---

## 2. What needs to be done

- [x] Pilot: 2 tracks (1 AI, 1 human), 1 model. The model leaned the right way at ~60% confidence.
- [x] Sanitisation pipeline (`scripts/sanitize.sh`) and leak checker (`scripts/verify.sh`)
- [x] Scoring script (`scripts/score.py`)
- [x] Pilot 2 (12 Oct): 10 tracks, 3 chat apps, 5 conditions. All at chance ([results/pilot_report.md](results/pilot_report.md))
- [x] Run 2 (16 Oct): difficulty ladder L0 / L2 / L4, 90 chats ([LEVELS_PLAN.md](LEVELS_PLAN.md), [results page](https://atharva-729.github.io/AI-music-detection-benchmark/))
- [ ] Ladder levels L1 and L3 (designed, not run)
- [ ] **Scale the dataset** (§3): target ≥ 50 AI + ≥ 50 human tracks (20 + 20 downloaded so far)
- [ ] Spot-listen the tracks to confirm vocal/instrumental labels
- [ ] Run every model under the protocol (§5), 3 runs per track, ideally through APIs with native audio input
- [ ] Optional: a non-LLM baseline (small CNN on mel spectrograms) for reference
- [ ] Optional: robustness rounds (§8)

---

## 3. Dataset

### Composition

Aim for **balanced classes** and **matched genres**, so a model can't win by guessing "orchestral = human, pop = AI".

| | AI-generated | Human-made |
|---|---|---|
| Count | ≥ 50 | ≥ 50 |
| Sources | Suno (several versions), Udio, any others available. Log the generator + version | Released tracks from a range of eras, genres and production budgets |
| Genres | Pop, rock, electronic, hip-hop, orchestral/cinematic, lo-fi, ambient, Indian film/indie | **Same genre mix as the AI side** |
| Vocals | Mix of vocal and instrumental | Same ratio as the AI side |

**Hard cases to include on purpose:**
- Human tracks that are loud, dense and heavily mastered (modern pop/EDM). These look "AI-ish" statistically.
- Human tracks from small or unknown artists (less chance the model recognises them).
- AI tracks that are sparse and dynamic (ambient, solo piano), which look "human-ish".
- AI tracks that were post-processed in a DAW (EQ, mastering).

**Avoid** very famous human songs: an LLM that recognises a track is doing identification, not detection.

### Folder layout

```
ai-music-bench/
├── raw/
│   ├── ai/          # original AI files (never shared)
│   └── human/       # original human files (never shared)
├── blind/           # sanitised clips, random IDs. This is all the models ever see
├── private/
│   └── key.csv      # answer key: track_id → label. Never upload this anywhere
├── results/
│   └── responses.csv
└── scripts/
    ├── sanitize.sh
    ├── verify.sh
    └── score.py
```

`raw/`, `blind/` and `private/` are git-ignored. Copyrighted audio stays internal. It is used for evaluation only and never redistributed.

---

## 4. Removing the giveaways (sanitisation)

### Requirements
`ffmpeg` (with libmp3lame), `ffprobe`, `python3`, `openssl`, `strings` (binutils).

### Two difficulty levels

| Level | What's normalised | Use it to test… |
|---|---|---|
| **A: format only** | Tags, encoder, bitrate, cutoff, sample rate, channels, filename, timestamps | Whether models can detect from the *full* track |
| **B: format + content-neutral** (default) | Everything in A, **plus** a fixed 30 s clip (starting 25% into the track) and loudness normalised to −16 LUFS | Whether models can detect from the *sound itself*, without length or loudness hints |

Report Level B as the headline result. Level A is a secondary run.

### Run it

```bash
# AI tracks (GENERATOR is optional, just logged in the key)
GENERATOR=suno-v4.5 scripts/sanitize.sh raw/ai ai B
GENERATOR=udio      scripts/sanitize.sh raw/ai_udio ai B

# Human tracks
scripts/sanitize.sh raw/human human B

# Check for leaks
scripts/verify.sh
```

`verify.sh` prints one row per clip. **Every column except the ID must match across all files**:

```
id              bitrate   dur_s     sr    ch   tags   enc_str
trk_33371443     191999  30.040  44100     2      1 LAME3.100
trk_53430dc1     191999  30.040  44100     2      1 LAME3.100
trk_5fed9c41     191999  30.040  44100     2      1 LAME3.100
```

(`LAME3.100` showing up in every file is fine. The encoder writes it as padding, and it's identical for every file, so it gives nothing away.)

### What the script does, per file

Single-file version, for when you just want to clean one track by hand (Level B; drop `-ss/-t` and the `loudnorm`/`afade` filters for Level A):

```bash
ffmpeg -ss 30 -t 30 -i input.mp3 \
  -map 0:a:0 -map_metadata -1 -map_chapters -1 \
  -fflags +bitexact -flags:a +bitexact \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.5,afade=t=out:st=29:d=1,aresample=44100,lowpass=f=15000:poles=2,lowpass=f=15000:poles=2" \
  -ac 2 -c:a libmp3lame -b:a 192k -cutoff 15500 \
  -write_xing 0 -id3v2_version 0 -write_id3v1 0 \
  output.mp3
touch -t 202601010000 output.mp3
```

| Flag(s) | Removes / equalises |
|---|---|
| `-map 0:a:0 -map_metadata -1 -map_chapters -1` | All tags, chapters, cover art, extra streams |
| `-fflags +bitexact -flags:a +bitexact` | ffmpeg version strings |
| `-ss … -t 30` | Duration (fixed 30 s clip; the script starts at 25% of the track) |
| `loudnorm=I=-16…` | Loudness (−16 LUFS) |
| `afade` in/out | Abrupt or distinctive start/end edges |
| `aresample=44100`, `-ac 2` | Sample rate, channel count |
| `lowpass=f=15000` (×2) | High-frequency cutoff (set below any source's own cutoff) |
| `libmp3lame -b:a 192k -cutoff 15500` | Encoder, version, bitrate, CBR/VBR mode |
| `-write_xing 0 -id3v2_version 0 -write_id3v1 0` | Xing/Info header, ID3 tags |
| `touch -t …` | File modification time |

The 15 kHz low-pass is deliberate. Different source encodes cut off at different frequencies (128 kbps ≈ 16 kHz, 320 kbps ≈ 19–20 kHz). Filtering everything below the lowest cutoff stops the frequency ceiling from revealing where a file came from.

### Things the script can't fix (handle them by hand)

- **Upload filenames**: some chat UIs show the original filename. Upload the `trk_xxxx.mp3` files only.
- **Track recognition**: handled through the prompt (the model must disclose it) and by choosing obscure tracks.
- **Invisible watermarks** (e.g. SynthID, AudioSeal) survive re-encoding. If a model could actually read one, that's a legitimate detection method, so leave them in. Just note it in the write-up.

---

## 5. Benchmark protocol

1. **One track per fresh conversation.** No chat history, no memory. Otherwise the model compares tracks against each other instead of judging each one on its own.
2. **Shuffle the order** of clips for each model.
3. **3 runs per track per model** (separate fresh chats) to measure consistency.
4. **No web search, no Shazam-style tools.** Turn off web search/browsing where possible. Code execution is allowed (a model that writes its own spectrogram analysis is fair game), but record whether it was used.
5. **Default settings**: whatever temperature and mode the consumer app uses. Record exact model name, version, interface (app vs API), and date.
6. **Paste the prompt below exactly.** Don't add hints.
7. If a model can't process audio, record `ABSTAIN` with confidence 50.
8. Log each answer as one row in `results/responses.csv`.

### The prompt

```text
You are taking part in a blind evaluation of AI-generated music detection.

Attached is one audio clip. It is EITHER fully AI-generated (made by a music
generation model such as Suno or Udio) OR human-made (composed, performed and
produced by people). It may be a short excerpt of a longer track.

Rules:
- Base your judgement only on the audio itself.
- Do NOT use web search, song-identification tools, or try to look the track up.
- All metadata, tags, filenames and encoder information have been removed or made
  identical across clips, so they carry no information.
- If you nevertheless recognise the song, you must say so in "identified_track".
- You may analyse the audio with code if you are able to.

Answer with ONLY the JSON object below, no other text:

{
  "verdict": "AI" or "HUMAN",
  "confidence": <integer 50-100: your probability (in %) that your verdict is
                 correct. 50 = pure guess, 100 = certain>,
  "identified_track": "yes" or "no",
  "identified_as": "<artist - title if yes, otherwise empty string>",
  "evidence": ["<up to 5 short, specific observations that drove your verdict>"],
  "used_code_analysis": "yes" or "no"
}

Calibrate carefully: across many clips, verdicts you give at 70% confidence
should be correct about 70% of the time. Overconfidence is penalised.
```

**Why confidence is 50–100, not 0–100:** it's the probability that *the verdict* is right, so anything below 50 would mean the model believes the opposite verdict. The scorer converts it to P(AI): `P(AI) = conf` if the verdict is AI, else `1 − conf`.

### `results/responses.csv` format

```csv
model,run,track_id,verdict,confidence,identified_track
claude-opus-5.5,1,trk_53430dc1,AI,60,no
gpt-x,1,trk_53430dc1,HUMAN,75,no
gemini-x,1,trk_53430dc1,ABSTAIN,50,no
```

Keep the full JSON answers (including `evidence`) in a separate log for the qualitative analysis.

---

## 6. Scoring

```bash
python3 scripts/score.py private/key.csv results/responses.csv
```

Example output (synthetic data, used to test the scorer):

```
model           n    acc  bal_acc ai_recall human_fpr  brier logloss  auroc   ece abstain identified consist  brier 95% CI
good-model    120  0.792    0.792     0.800     0.217  0.169   0.517  0.828 0.080   0.000      0.000    0.47  [0.138, 0.201]
coinflip      120  0.417    0.417     0.367     0.433  0.307   0.831  0.466 0.197   0.117      0.000    0.28  [0.267, 0.346]
overconfident 120  0.517    0.517     0.533     0.500  0.438   1.474  0.517 0.433   0.000      0.000    0.23  [0.355, 0.520]
Reference: always-50% guesser -> brier 0.250, logloss 0.693, auroc 0.500
```

### Metrics

| Metric | What it tells us | Good value |
|---|---|---|
| **Brier score** (primary) | Mean of (P(AI) − truth)². Rewards being right *and* calibrated. Punishes confident mistakes hard | Lower is better. **0.25 = the always-50% guesser.** Anything above 0.25 is worse than not answering |
| Balanced accuracy | Accuracy averaged over the AI and human classes, so it can't be gamed by always saying "AI" | > 0.5 |
| AI recall | Share of AI tracks caught | High |
| **Human false-positive rate** | Share of human tracks wrongly called AI. **This matters most for publishing**, because falsely accusing an artist is worse than missing an AI track | Low |
| AUROC | Can the model *rank* AI above human, regardless of threshold? | > 0.5 (0.5 = chance) |
| Log loss | Like Brier, but punishes 100%-confident mistakes even harder (probabilities clipped to 1–99%) | Lower; 0.693 = chance |
| ECE (calibration error) | Gap between stated confidence and actual accuracy, across confidence bins | Lower; 0 = perfectly calibrated |
| Abstain rate | Share of clips the model couldn't or wouldn't judge | Report it, don't hide it |
| Identified rate | Share of clips the model claimed to recognise. **Results on those clips are contaminated** | Report, and re-score with these excluded |
| Consistency | Share of tracks that got the same verdict in all 3 runs | Higher = more stable |
| Brier 95% CI | Bootstrap over tracks. If two models' intervals overlap heavily, don't call a winner | — |

### Leaderboard rule

Rank by **Brier score on Level B, with identified tracks excluded**. Break ties with human FPR.

### Sample size reality check

With 100 tracks, a model with true accuracy 70% will measure somewhere in about 61–79%. Fewer than ~50 tracks per class can't separate models that are close. Use the bootstrap CI before claiming one model beats another.

---

## 7. Results

### Pilot (n = 2, Level ≈ A, informal)

| Track | Truth | Claude's lean | Confidence | Main reasoning |
|---|---|---|---|---|
| `out.mp3` | AI | AI | ~60% | Uniform, dense, heavily compressed texture; few section changes |
| `out1.mp3` | Human | Human | ~60% | Stepwise arrangement, 26 dB loudness range, clean fade (+ an old-encoder leak, since fixed) |

The verdicts were correct, but n = 2 says nothing statistically. The pilot's real value was finding the leak list in §1.

### Pilot 2 (n = 10, 12 Oct)

Every model and setting landed at chance (40–50% correct). See [results/pilot_report.md](results/pilot_report.md).

### Run 2: difficulty ladder (n = 10 per cell, 16 Oct)

Correct out of 10 (chance = 5). Full tables, examples, token estimates and caveats are on the **[results page](https://atharva-729.github.io/AI-music-detection-benchmark/)**.

| Level | ChatGPT | Claude | Gemini |
|---|---|---|---|
| L0 raw file (tags intact) | 10 | 10 | 6 |
| L2 same format, full length | 4 | 7 | 6 |
| L4 30 s clip, loudness-matched | 5 | 6 | 6 |

ChatGPT and Claude detect only by reading embedded tags with code; once the tags are gone, all three models are at chance.

### Round 3: vocal songs from older generators (17 Oct)

5 SONICS songs (Suno v3.5 / Udio, AI-written lyrics) vs 5 human CC vocal tracks, all at identical 16 kHz mono quality, 30 s clips.

| | ChatGPT | Claude | Gemini |
|---|---|---|---|
| Correct of 10 | 5 | 6 | 7 (all 5 AI caught, perfect ranking) |

Gemini's signal may come from the AI-written lyrics it cites. A 2-file frequency test found that full high-frequency content did not make any model call a human song human.

---

## 8. Stretch goals

- **Robustness rounds:** re-run on perturbed clips (64 kbps re-encode, ±1 semitone pitch shift, added noise, phone-speaker re-recording). These are the attacks that broke dedicated detectors in Deezer's research.
- **Non-LLM baseline:** a small CNN on mel spectrograms trained on a separate split, to show how a cheap purpose-built detector compares with general LLMs.
- **Evidence audit:** tag each model's `evidence` lines as *audio-grounded* ("vocal breaths sound smeared at 0:12") or *generic* ("sounds polished"). Do confident-and-correct answers cite real evidence?
- **Generator breakdown:** accuracy per generator/version. Are newer models harder to catch?
- **Same benchmark for images and text** (same blind/score setup, different sanitiser), to make it a general "AI-content detection" evaluation for the publishing side.

---

## 9. Risks & caveats

- **This measures detection under lossy, normalised conditions.** Real-world files are often cleaner, which makes detection easier. A poor score here doesn't mean detection is impossible.
- **Model versions change silently.** Always record the date and version; results go stale.
- **Copyright:** evaluation-only internal use; never commit or share audio.
- **Generator terms of service:** check Suno/Udio terms for the account used to make the AI tracks.
- **Stated confidence ≠ real uncertainty.** LLMs often give round numbers (70, 80, 90). The ECE metric shows how much that matters.
