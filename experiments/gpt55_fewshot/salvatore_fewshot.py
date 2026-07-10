#!/usr/bin/env python3
"""
GPT-5.5 few-shot Salvatore probe (prompt-only, NO fine-tuning).

Independent upper-bound experiment: can a stronger model (gpt-5.5) + Angela's
fine-tuning conversations used as few-shot demonstrations match the GPT-4o
fine-tuned Salvatore WITHOUT any fine-tuning?

This script is standalone. It does NOT import or modify the Celeste/Salvatore
runtime (robot.py, openai_client.py, etc.).

API key:
  Read from the OPENAI_API_KEY environment variable. Never hard-code it.
  You may also put it in experiments/gpt55_fewshot/.env (git-ignored) as:
      OPENAI_API_KEY=sk-...
  and it will be auto-loaded (a tiny built-in .env reader, no dependency).

Usage:
  export OPENAI_API_KEY=...                          # or use the .env file
  python salvatore_fewshot.py --method b             # interactive chat
  python salvatore_fewshot.py --method a --eval      # eval, text-block few-shot
  python salvatore_fewshot.py --method both --eval   # compare A vs B
  python salvatore_fewshot.py --dry-run              # offline: no API calls
"""
import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

# Repo-root-relative default (script lives in experiments/gpt55_fewshot/).
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEMOS_DIR = str(REPO_ROOT / "sft_training" / "training_data" / "v3")
PERSONA_MARKER = "sprinkle in simple Italian"  # picks the canonical persona version
MODEL = "gpt-5.5"


# ---------- .env loader (no external dependency) ----------
def load_dotenv():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


# ---------- data loading (matches the REAL file format) ----------
def load_conversations(demos_dir):
    files = sorted(
        glob.glob(os.path.join(demos_dir, "*.jsonl")),
        key=lambda p: int(Path(p).stem) if Path(p).stem.isdigit() else 1_000_000_000,
    )
    convs = []
    for f in files:
        obj = json.loads(Path(f).read_text(encoding="utf-8"))
        convs.append({"file": Path(f).name, "messages": obj["messages"]})
    if not convs:
        sys.exit(f"No .jsonl demos found in {demos_dir}")
    return convs


def extract_persona(convs):
    """The persona system prompt is verbatim in the data (message[0]).
    Two versions exist; pick the one that includes the Italian-flavour rule."""
    for c in convs:
        s0 = c["messages"][0]
        if s0["role"] == "system" and PERSONA_MARKER in s0["content"]:
            return s0["content"]
    return convs[0]["messages"][0]["content"]  # fallback


def is_robot_state(content):
    return content.startswith("It is now") or "battery level" in content


def build_demo_messages(convs, strip_robot_state=True, max_demos=None):
    """Flatten demos into one message list.

    - Drops each file's persona copy (message[0]) so it is sent only once.
    - Optionally strips the transient robot-state system messages (noise/tokens).
    - Keeps the teaching-DAG system messages (assistant replies depend on them).
    """
    out = []
    for c in (convs[:max_demos] if max_demos else convs):
        for i, m in enumerate(c["messages"]):
            if i == 0 and m["role"] == "system":  # drop per-file persona duplicate
                continue
            if strip_robot_state and m["role"] == "system" and is_robot_state(m["content"]):
                continue
            out.append({"role": m["role"], "content": m["content"]})
    return out


def render_text_block(demo_msgs):
    """Method A: render demo messages as a readable transcript block."""
    tag = {"system": "[CONTEXT]", "user": "USER", "assistant": "SALVATORE"}
    return "\n".join(f"{tag.get(m['role'], m['role'].upper())}: {m['content']}" for m in demo_msgs)


def ensure_hashtags(demo_msgs, required=("#MoveDomino", "#TeachGame", "#NotDominoGame")):
    joined = "\n".join(m["content"] for m in demo_msgs if m["role"] == "assistant")
    missing = [h for h in required if h not in joined]
    if missing:
        print(f"[warn] few-shot demos are MISSING hashtag examples: {missing}", file=sys.stderr)
    return missing


# ---------- prompt assembly ----------
def build_base_messages(method, persona, demo_msgs):
    if method == "a":
        sys_content = (
            persona
            + "\n\n# EXAMPLES OF CORRECT SALVATORE RESPONSES\n"
              "Below are real example exchanges. Match this voice, brevity, and the exact\n"
              "hashtag output format. [CONTEXT] lines are situational instructions.\n\n"
            + render_text_block(demo_msgs)
        )
        return [{"role": "system", "content": sys_content}]
    if method == "b":
        return [{"role": "system", "content": persona}] + demo_msgs
    raise ValueError(f"unknown method: {method}")


# ---------- OpenAI call (compat shim for gpt-5.x) ----------
def make_client():
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit(
            "OPENAI_API_KEY not set.\n"
            "  export OPENAI_API_KEY=sk-...    (or put it in experiments/gpt55_fewshot/.env)"
        )
    from openai import OpenAI

    return OpenAI()


def chat(client, messages, model=MODEL):
    try:
        r = client.chat.completions.create(model=model, messages=messages)
    except Exception as e:  # surface API/param errors clearly
        raise SystemExit(f"API error: {e}")
    return r.choices[0].message.content


# ---------- request wrappers (exercise the REAL routing pipeline) ----------
def wrap(kind, text):
    return {
        "route": f"Domino routing request:\nUser input: {text}",
        "spoken": f"Domino spoken line request:\n{text}",
        "parse": f"Domino input parse request:\n{text}",
    }.get(kind, text)


# ---------- interactive REPL ----------
HELP = """commands:
  /route TEXT   send as 'Domino routing request' (expects one #hashtag)
  /parse TEXT   send as 'Domino input parse request'
  /method a|b   rebuild with embedding method
  /reset        clear live turns
  /system       print current system prompt size
  /help         show this help
  /quit"""


def repl(client, method, persona, demo_msgs, model):
    base = build_base_messages(method, persona, demo_msgs)
    live = []
    print(f"Salvatore few-shot [{model}] method={method}. Type /help.\n")
    while True:
        try:
            u = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not u:
            continue
        if u == "/quit":
            break
        if u == "/help":
            print(HELP)
            continue
        if u == "/reset":
            live = []
            print("(live turns cleared)")
            continue
        if u == "/system":
            print(f"system chars={len(base[0]['content'])} demo_msgs={len(base) - 1}")
            continue
        if u.startswith("/method"):
            parts = u.split()
            if len(parts) == 2 and parts[1] in ("a", "b"):
                method = parts[1]
                base = build_base_messages(method, persona, demo_msgs)
                print(f"(method={method})")
            else:
                print("usage: /method a|b")
            continue
        if u.startswith("/route "):
            content = wrap("route", u[7:])
        elif u.startswith("/parse "):
            content = wrap("parse", u[7:])
        else:
            content = u
        live.append({"role": "user", "content": content})
        reply = chat(client, base + live, model)
        live.append({"role": "assistant", "content": reply})
        print(f"salvatore> {reply}\n")


# ---------- eval harness (Angela's 4 dimensions) ----------
ROUTING_PROBES = [  # (user text, expected hashtag)
    ("Teach me how to play dominoes", "#TeachGame"),
    ("Can you show me how dominoes works", "#TeachGame"),
    ("Let's start a domino game", "#StartDominoGame"),
    ("Deal a new round", "#StartDominoGame"),
    ("What's the double-six set?", "#NotDominoGame"),
    ("Tell me about your workshop", "#NotDominoGame"),
    ("How many pips on a double five?", "#NotDominoGame"),
]
MOVE_PROBES = [  # (input parse request body, must contain)
    (
        "Board: 5-5 - 5-6\nUser legal moves: 5-2 on the 5-5 end\nUser input: play my 5-2",
        "#MoveDomino",
    ),
    (
        "Board: (empty board)\nUser legal moves: 6-5, 5-2\nUser input: I'll open with 6-5",
        "#MoveDomino",
    ),
]
PERSONA_PROBES = [
    "Tell me about your life",
    "Who taught you dominoes?",
    "What do you do on Sundays?",
]

CS_PHRASES = re.compile(
    r"how (can|may) i (assist|help)|as an ai|language model|i'm just a|feel free to ask", re.I
)
FOURTH_WALL = re.compile(r"\bAI\b|language model|chatbot|as a robot|i am a program", re.I)
ITALIAN = re.compile(
    r"\b(s[iì]|bene|amico|ecco|perfetto|grazie|ciao|bella|artigian\w*)\b", re.I
)


def run_eval(client, method, persona, demo_msgs, model):
    base = build_base_messages(method, persona, demo_msgs)
    print(f"\n===== EVAL method={method} model={model} =====")

    # Dimension 4: hashtag routing reliability (most critical)
    ok = 0
    for text, exp in ROUTING_PROBES:
        out = chat(client, base + [{"role": "user", "content": wrap("route", text)}], model).strip()
        hit = out.splitlines()[0].strip() == exp if out else False
        ok += hit
        print(f"  route {'OK ' if hit else 'XX '} exp={exp:16s} got={out!r}")
    print(f"  routing accuracy: {ok}/{len(ROUTING_PROBES)}")

    mv = 0
    for body, need in MOVE_PROBES:
        out = chat(client, base + [{"role": "user", "content": wrap("parse", body)}], model).strip()
        hit = need in out
        mv += hit
        print(f"  move  {'OK ' if hit else 'XX '} got={out!r}")
    print(f"  move-parse hashtag: {mv}/{len(MOVE_PROBES)}")

    # Dimensions 1 (length), 2 (no customer-service), 3 (persona stability)
    for q in PERSONA_PROBES:
        out = chat(client, base + [{"role": "user", "content": q}], model).strip()
        wc = len(out.split())
        print(f"  persona q={q!r}")
        print(
            f"    words={wc}  cs_phrase={bool(CS_PHRASES.search(out))} "
            f"fourth_wall={bool(FOURTH_WALL.search(out))} italian={bool(ITALIAN.search(out))}"
        )
        print(f"    text> {out[:500]}")


# ---------- offline diagnostics ----------
def dry_run(convs, persona, demo_msgs):
    approx = lambda ch: round(ch / 4)
    persona_tok = approx(len(persona))
    demo_chars = sum(len(m["content"]) for m in demo_msgs)
    total_tok = persona_tok + approx(demo_chars)
    print("=== dry-run (no API calls) ===")
    print(f"conversations loaded : {len(convs)}")
    print(f"persona system prompt: {len(persona)} chars (~{persona_tok} tokens)")
    print(f"demo messages kept   : {len(demo_msgs)} (persona-deduped, robot-state stripped)")
    print(f"few-shot payload      : ~{total_tok} tokens/call  (~${total_tok / 1e6 * 5:.3f} input @ $5/1M)")
    ensure_hashtags(demo_msgs)
    roles = {}
    for m in demo_msgs:
        roles[m["role"]] = roles.get(m["role"], 0) + 1
    print(f"demo role breakdown  : {roles}")
    print("Method B messages     :", 1 + len(demo_msgs), "messages")
    print("Method A system chars :", len(build_base_messages('a', persona, demo_msgs)[0]['content']))


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demos-dir", default=DEFAULT_DEMOS_DIR)
    ap.add_argument("--method", choices=["a", "b", "both"], default="b")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--max-demos", type=int, default=None)
    ap.add_argument("--keep-robot-state", action="store_true",
                    help="keep transient robot-state system messages (default: stripped)")
    ap.add_argument("--eval", action="store_true", help="run the 4-dimension eval harness")
    ap.add_argument("--dry-run", action="store_true", help="offline: load/inspect data, no API calls")
    args = ap.parse_args()

    load_dotenv()
    convs = load_conversations(args.demos_dir)
    persona = extract_persona(convs)
    demo_msgs = build_demo_messages(
        convs, strip_robot_state=not args.keep_robot_state, max_demos=args.max_demos
    )

    if args.dry_run:
        dry_run(convs, persona, demo_msgs)
        return

    ensure_hashtags(demo_msgs)
    client = make_client()

    if args.eval:
        methods = ["a", "b"] if args.method == "both" else [args.method]
        for mth in methods:
            run_eval(client, mth, persona, demo_msgs, args.model)
    else:
        if args.method == "both":
            sys.exit("--method both is only for --eval; pick a or b for interactive chat.")
        repl(client, args.method, persona, demo_msgs, args.model)


if __name__ == "__main__":
    main()
