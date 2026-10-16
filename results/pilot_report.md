# Pilot report: can chat LLMs tell AI music from human music?

Date: 12 October 2026 · Status: **pilot complete on 10 tracks, three models, five conditions**

## Summary

- **No model or setting beat chance.** Across five conditions, accuracy was 40–50% on a balanced set of 5 AI and 5 human tracks.
- **Every Brier score was worse than not answering.** Scores ran from 0.270 to 0.437, against 0.250 for always answering 50%.
- **Giving ChatGPT the full song instead of a 30-second clip changed nothing.** It got 5 of 10 right both ways.
- **Turning ChatGPT's thinking mode on did not help.** With two clips per chat it got 4 of 10 right and labelled one clip AI and one human in every pair, whatever the pair contained.
- **Each model fails in its own way.** ChatGPT leans "AI", Gemini leans "HUMAN" with high confidence and invented two track identifications, and Claude says it cannot hear the audio and gives near coin-flip answers from spectrum statistics.
- **Claude's evidence is partly our own processing.** It repeatedly cited the 16 kHz cutoff and the fade-out, both of which the sanitiser adds to every clip.

Ten tracks is a smoke test, not a measurement, and the task is hard: the project owner also finds these tracks difficult to tell apart by ear, especially from 30 seconds. The consistent result is still worth acting on: under these conditions, none of these verdicts tells you anything about the track.

## What was run

Ten tracks: 5 AI (Suno v5 / v5.5) and 5 human (Creative Commons, uploaded before 2022), as 5 style-matched pairs (lo-fi chillhop, UK garage / house-pop, jazzy trap, afro house, dub techno).

| Condition | Model and settings | Audio | Chats |
|---|---|---|---|
| A. ChatGPT, clips | chatgpt.com (Go plan), temporary chat, memory ignored, Think off | 30 s clip | 1 clip per chat |
| B. Gemini, clips | gemini.google.com, temporary chat, 3.8 Flash, thinking level Low (default) | 30 s clip | 1 clip per chat |
| C. ChatGPT, Think on | As A, with Think on | 30 s clip | 2 clips per chat, prompt adapted |
| D. ChatGPT, full song | As A | Full track, 1m44s to 9m29s | 1 track per chat |
| E. Claude, clips | claude.ai (Pro plan), normal chat with memory off, Sonnet 5.5, Medium effort | 30 s clip | 1 clip per chat |

- The 30-second clips are Level B: fixed length, loudness-normalised, 192 kbps.
- The full tracks are Level A: same tag and encoder clean-up, but no trimming or loudness change, at 128 kbps so the longest fits the upload limit. Length and loudness therefore differ between tracks.
- One run per item. The README prompt was used unchanged except in condition C.
- ChatGPT does not display its model name; it is recorded as GPT 5.6 Luna on the owner's word.
- Claude's incognito mode rejects MP3 uploads, so Claude ran in normal chats.

## Results

| Metric | A. ChatGPT clips | B. Gemini clips | C. ChatGPT Think, paired | D. ChatGPT full song | E. Claude clips | Reference |
|---|---|---|---|---|---|---|
| Correct | 5 of 10 | 4 of 10 | 4 of 10 | 5 of 10 | 4 of 10 | 5 = chance |
| AI tracks caught | 5 of 5 | 0 of 5 | 2 of 5 | 4 of 5 | 3 of 5 | |
| Human tracks called AI | 5 of 5 | 1 of 5 | 3 of 5 | 4 of 5 | 4 of 5 | lower is better |
| Brier score | 0.274 | 0.437 | 0.294 | 0.270 | 0.272 | 0.250 = always 50% |
| Brier 95% CI | 0.173–0.374 | 0.223–0.653 | 0.220–0.369 | 0.194–0.350 | 0.232–0.310 | |
| AUROC | 0.60 | 0.48 | 0.24 | 0.40 | 0.36 | 0.50 = chance |
| Calibration error (ECE) | 0.225 | 0.446 | 0.385 | 0.208 | 0.160 | 0 = perfect |
| Confidence range | 64–70% | 75–95% | 59–66% | 58–66% | 52–60% | |
| Claimed to recognise the track | 0 | 2 (both false) | 0 | 0 | 0 | |
| Used code | 10 of 10 | 0 of 10 | 8 of 10 | 10 of 10 | 10 of 10 | |

The intervals overlap, so this pilot does not rank the conditions. Gemini's low false-positive count is not a strength: it comes from answering "HUMAN" nine times out of ten.

## How much of the song does the model need?

ChatGPT was given the same 10 tracks as 30-second clips (A) and as full songs (D), with the same settings.

| | 30 s clip | Full song |
|---|---|---|
| Correct | 5 of 10 | 5 of 10 |
| Verdicts | 10 AI, 0 human | 8 AI, 2 human |
| Brier score | 0.274 | 0.270 |
| Confidence range | 64–70% | 58–66% |

- More audio did not improve detection.
- The only change was two "HUMAN" verdicts, both on the dub techno pair (one right, one wrong). Those are two of the three longest tracks, so track length may have driven the answer.
- The full-song condition also leaks loudness and duration, which the 30-second condition removes. Even with those extra cues available, accuracy did not move.

## What thinking mode changed

With Think on and two clips per chat (C), ChatGPT called one clip AI and the other human in all 5 chats, including the pair where both were AI and the pair where both were human. In the three mixed pairs it got two backwards. It did run more real analysis (stereo correlation, spectral statistics), but the outcome was no better. Because two things changed at once (thinking and pairing), this condition cannot separate their effects.

## What each model's evidence shows

**ChatGPT**
- Described vocals on 5 of the 6 clips labelled instrumental, and "rock instrumentation", "guitars" or a "singer-songwriter presentation" on dub techno and jazzy trap tracks.
- Used near-identical wording throughout: smooth vocal timbre, polished mix, "suggestive rather than conclusive".
- With Think off, the code that was captured loaded the file and rendered an audio player, and computed no features.

**Gemini**
- Identified an AI jazzy trap clip as "Childish Gambino - Redbone" and a human jazzy trap clip as "The Chemical Brothers - Block Rockin' Beats". Both are false, and it cited specific details of those songs.
- Justified "HUMAN" almost every time with the absence of artefacts. The one time it reported those artefacts, the clip was human.

**Claude**
- Stated in three answers that it cannot listen to audio, and in the rest that it relied only on spectrum and loudness statistics. Several answers called the verdict "close to a coin flip".
- All 10 answers mention the hard cutoff near 16 kHz. Five correctly dismissed it as shared encoding; the others read it as a cue, mostly towards AI. That cutoff is the low-pass filter the sanitiser applies to every clip.
- Two answers cited the fade-out at the end of the clip, which the sanitiser also adds.
- Its confidence (52–60%) was the most honest of the three, which is why its calibration error is the lowest.

Both ChatGPT and Gemini described vocals on the same number of "instrumental" clips. The labels come from track metadata and were not checked by ear, so they may be wrong. This needs a listen before the vocal mismatch is used as evidence.

## Time and effort

Only the Claude runs were timed. The rest are estimates from how long each answer took to appear during the run, and are marked as such.

| Condition | Time per answer | Basis | Model effort |
|---|---|---|---|
| A. ChatGPT clips | about 30–50 s | Estimate. Every answer arrived inside a 50 s wait; one chat showed "Worked for 26s" | Think off; loaded the file with code |
| B. Gemini clips | about 20–40 s | Estimate. Most answers arrived inside 30 s, the rest inside 40 s | Thinking level Low; no code |
| C. ChatGPT Think, paired | about 2–2.5 min per chat (2 clips) | Estimate from polling | Think on; several rounds of code in at least one chat |
| D. ChatGPT full song | about 50–110 s | Estimate. One chat showed "Worked for 30s"; two needed about 110 s | Think off; 4–5 code steps per track |
| E. Claude clips | 19–24 s, mean 21 s | Measured in the page for 9 of 10 runs; the first was under 50 s | Medium effort; 2–3 code commands per clip |

- **Total model time** was roughly 40 minutes across the 50 answers: about 7 minutes for A, 5 for B, 11 for C, 12 for D and under 4 for E.
- **End-to-end time** including opening each chat, uploading and reading the answer was longer, roughly 1.5–3 minutes per chat. This was not timed.
- **Cost** cannot be read from these runs. The consumer apps show no token counts, so there is no spend figure beyond the existing subscriptions, and how much of each plan's usage allowance the runs consumed is not visible.
- Response time is now captured automatically for each run, so later runs will have measured figures.

## Limits of this pilot

- 10 tracks and one run per item: no consistency measure and wide intervals on every metric.
- 30-second clips are hard to judge even for a human listener; the owner finds these tracks difficult to tell apart.
- Consumer apps, with the model version not shown (ChatGPT) or settings chosen by the app (Gemini's thinking level).
- Human tracks were chosen from metadata, not by listening.
- The sanitiser's own low-pass filter and fades were picked up as evidence by Claude, so they are not neutral for a model that analyses the signal with code.
- Conditions differ in more than one way: C changes thinking and pairing together, and D changes length, loudness handling and bitrate together.
- Two ChatGPT items and one early Gemini attempt were re-run after an answer was lost or the upload failed; only the completed run is recorded.
- The 10 Claude chats are in the owner's normal chat history.

## Next steps

1. **Test whether the models hear the audio at all.** Ask each to describe one clip (tempo, instruments, vocals or not) with no detection question. Claude has already said it cannot.
2. **Spot-listen the 10 pilot tracks** to confirm which have vocals.
3. **Decide whether the remaining 30 tracks are worth running** on these apps, given every condition landed at chance.
4. **If the study continues, change one variable at a time** (length only, or thinking only), and consider models with native audio input through an API, which is where real listening is most likely.

## Files

- `results/responses.csv`: 40 scored answers for the 30-second conditions (A, B, C, E).
- `results/responses_full.csv`: 10 scored answers for the full-song condition (D), scored against `private/key_full.csv`.
- `results/pilot_raw_log.jsonl`: full JSON answers with evidence, settings, timings where measured, and run notes.
- `results/pilot_runsheet.md`: clip order per model.
- `private/pilot_slots.csv`, `private/key_full.csv`: answer keys (not committed).
