# GPT-5.5 few-shot Salvatore (prompt-only, no fine-tuning)

Upper-bound probe: can `gpt-5.5` + Angela's SFT conversations used as **few-shot
demonstrations** match the GPT-4o **fine-tuned** Salvatore, with **no fine-tuning**?

Standalone. Does **not** touch the Celeste/Salvatore runtime (`robot.py`,
`openai_client.py`).

## Where to put your API key

Pick ONE:

1. **Environment variable** (recommended for one-off runs):
   ```bash
   export OPENAI_API_KEY=sk-...
   ```
2. **`.env` file** (recommended for repeated runs) — create
   `experiments/gpt55_fewshot/.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```
   Copy `.env.example` to `.env` and fill it in. `.env` is git-ignored, so the
   key never gets committed. The script auto-loads it (no dependency needed).

The key is only read via `os.getenv("OPENAI_API_KEY")` — never hard-coded.

## Run

```bash
cd experiments/gpt55_fewshot

# offline sanity check (no API calls, no key needed):
python salvatore_fewshot.py --dry-run

# interactive chat, multi-turn message few-shot (method B):
python salvatore_fewshot.py --method b

# interactive chat, text-block few-shot (method A):
python salvatore_fewshot.py --method a

# eval harness on Angela's 4 dimensions, compare A vs B:
python salvatore_fewshot.py --method both --eval
```

Requires `openai` (already in the repo's requirements).

## In-chat commands

```
/route TEXT   send as 'Domino routing request' (expects one #hashtag)
/parse TEXT   send as 'Domino input parse request'
/method a|b   switch few-shot embedding method
/reset        clear live turns
/system       print current system prompt size
/quit
```

Use `/route ...` and `/parse ...` to test the **hashtag routing** exactly like
the real runtime (that is the most important, game-critical dimension).

## What the eval measures (Angela's 4 dimensions)

1. **Output length** — word count of persona replies (no long monologues).
2. **No customer-service tone** — regex for "how may I assist" etc.
3. **Persona stability** — Italian flavour present, no 4th-wall breaks (AI/robot).
4. **Hashtag routing reliability** — first line exactly equals expected
   `#TeachGame` / `#StartDominoGame` / `#NotDominoGame`, and `#MoveDomino`
   appears for move-parse probes. **Most critical**: game logic depends on it.

## Design notes (from reading the real data)

- The persona system prompt (~6.7K tokens) is verbatim in each file's
  `messages[0]`; it is extracted once and **deduped**, cutting input from
  ~299K to ~52K tokens/call (~$0.26 vs ~$1.49 at $5/1M input).
- Two persona versions exist in the data; the canonical one (with the Italian
  flavour rule) is selected via a marker string.
- Transient robot-state system messages (`"It is now ... battery ..."`) are
  stripped by default (noise/tokens); teaching-DAG system messages are kept
  because assistant replies depend on them.
- `#MoveDomino` has only ~7 examples in the whole set; `ensure_hashtags` warns
  if few-shot filtering ever drops it.
