# Salvatore TTS audition

Standalone OpenAI TTS voice × instructions audition matrix. It does not import or
modify the robot runtime.

## Run

From the repository root:

```bash
export OPENAI_API_KEY=sk-...
python3 experiments/tts_audition/audition.py
open experiments/tts_audition/out/index.html
```

Alternatively, copy `.env.example` to `.env` in this directory and put the key
there. The script loads that file without extra dependencies. Both `.env` and the
generated `out/` directory are git-ignored.

The default quick matrix creates 4 clips (1 clip per instruction variant):

- 1 voice: `cedar`
- 4 instruction variants: `v0` through `v3`
- 1 line: `greeting`

Useful options:

```bash
# Generate all 168 clips (6 voices × 4 variants × 7 lines)
python3 experiments/tts_audition/audition.py --full

# Generate selected dimensions
python3 experiments/tts_audition/audition.py --voices cedar,fable --variants v0,v2

# Generate 4 clips per instruction variant
python3 experiments/tts_audition/audition.py --voices cedar,fable --lines greeting,exclaim1

# Select lines explicitly (overrides the quick/full line set)
python3 experiments/tts_audition/audition.py --lines teaching,story,italian_mix

# Regenerate existing files
python3 experiments/tts_audition/audition.py --force

# Fail faster if a TTS request stalls
python3 experiments/tts_audition/audition.py --timeout 30 --max-retries 0
```

Existing non-empty MP3 files are skipped unless `--force` is supplied. API
failures are recorded in `out/failures.csv` and do not stop the remaining
matrix. Generation timing and file size are written to `out/latency.csv`. Each
clip prints a `START` line before the API request and a `DONE` or `FAILED` line
afterward, so progress is visible while the matrix runs.

## Listen and score

Open `out/index.html` in a browser. Matrix mode exposes every identity for direct
comparison and includes a **Download MP3** link for each generated clip.
Blind-listening mode randomizes the generated clips, hides the
identity until playback finishes, and lets you choose a 1–5 score. Click
**Save rating** to store the score in browser `localStorage`. Use **Export
ratings CSV** to download the saved scores.

## Add an instruction hypothesis

Edit the `VARIANTS` dictionary near the top of `audition.py`:

```python
VARIANTS = {
    # Existing variants...
    "v4": "Your new voice direction here.",
}
```

Then run `--variants v4` (optionally with a smaller voice or line subset). Keep
variant keys lowercase and filename-safe.
