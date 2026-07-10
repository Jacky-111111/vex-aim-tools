#!/usr/bin/env python3
"""Generate a Salvatore TTS audition matrix and a static blind-listening page."""

import argparse
import csv
import html
import json
import os
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "out"
MODEL = "gpt-4o-mini-tts-2025-03-20"

TEST_LINES = {
    "greeting": (
        "Buongiorno, amico! I am well, thank you - fine hands, clear eyes, and a steady "
        "heart. What brings you to Bottega Ferrante today?"
    ),
    "teaching": (
        "Bene! Now, in my workshop, we say the heavier end first. A tile with six pips "
        "on one side and three on the other, we call a six-three, not a three-six."
    ),
    "exclaim1": "Perfetto, you have it!",
    "exclaim2": "Ah, bone on ebony - nothing else compares.",
    "gameplay": (
        "You play the six-three on the three end - bravo! Now the board stretches "
        "three-three to three-six, so your next domino must match either a three or a six."
    ),
    "story": (
        "Certo! Very little in my life - just some trips to Naples for supplies and a "
        "journey or two to Rome for a fair. My father taught me the craft in this very "
        "workshop, and his father before him."
    ),
    "italian_mix": (
        "Benvenuto, amico mio! Today, we begin with the basics. Si, patience - a good "
        "domino, like a good day, cannot be rushed."
    ),
}

# Add new hypotheses here. The dictionary key becomes the CLI/filename variant name.
VARIANTS = {
    "v0": (
        "Speak English with a very strong, unmistakable Italian accent. "
        "Use Italian vowel timing, pronounced rolled R sounds, and Italian-style melody. "
        "Keep delivery concise and somewhat taciturn, like an elderly Italian man. "
        "Use a slightly higher register than typical elderly male speech. "
        "Keep the accent going for the entire dialogue, and never default to a generic "
        "American accent."
    ),
    "v1": (
        "Speak English with a very strong, unmistakable Italian accent. "
        "Use Italian vowel timing, pronounced rolled R sounds, and Italian-style melody. "
        "Warm, patient, and grandfatherly, with an audible smile - like welcoming an old "
        "friend into his workshop. "
        "Use a slightly higher register than typical elderly male speech. "
        "Keep the accent going for the entire dialogue, and never default to a generic "
        "American accent."
    ),
    "v2": (
        "Speak English the way an elderly craftsman from Sorrento who learned English late "
        "in life naturally would: authentic Italian prosody and vowel timing, gently rolled "
        "r's, unhurried pacing with small pauses. Authentic rather than theatrical. "
        "Pronounce Italian words (Buongiorno, amico, perfetto, certo) with native Italian "
        "pronunciation. Never drift into a generic American accent."
    ),
    "v3": (
        "Speak English with a very strong, unmistakable Italian accent. "
        "Use Italian vowel timing, pronounced rolled R sounds, and Italian-style melody. "
        "Keep delivery concise and somewhat taciturn, like an elderly Italian man. "
        "An aged, slightly weathered voice; relaxed pace with small pauses for breath. "
        "Keep the accent going for the entire dialogue, and never default to a generic "
        "American accent."
    ),
}

VOICES = ("cedar", "fable", "ash", "onyx", "echo", "verse")
QUICK_VOICES = ("cedar",)
QUICK_LINES = ("greeting",)
LATENCY_FIELDS = ("voice", "variant", "line", "seconds", "bytes")
FAILURE_FIELDS = ("voice", "variant", "line", "error")


def load_dotenv():
    """Load this experiment's .env without overriding exported variables."""
    env_path = SCRIPT_DIR / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def selected_values(raw, available, option_name):
    if raw is None:
        return list(available)
    values = [value.strip().lower() for value in raw.split(",") if value.strip()]
    unknown = [value for value in values if value not in available]
    if unknown:
        choices = ", ".join(available)
        raise SystemExit(
            f"Unknown {option_name}: {', '.join(unknown)}. Available values: {choices}"
        )
    return list(dict.fromkeys(values))


def read_keyed_csv(path, fields):
    records = {}
    if not path.exists():
        return records
    try:
        with path.open(newline="", encoding="utf-8") as csv_file:
            for row in csv.DictReader(csv_file):
                if all(field in row for field in fields):
                    records[(row["voice"], row["variant"], row["line"])] = row
    except (OSError, csv.Error):
        print(f"[warn] Could not read {path}; it will be rebuilt.", file=sys.stderr)
    return records


def write_csv(path, fields, records):
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        for key in sorted(records):
            writer.writerow({field: records[key].get(field, "") for field in fields})


def audio_filename(voice, variant, line):
    return f"{voice}__{variant}__{line}.mp3"


def create_audio(client, voice, instructions, text, destination):
    temporary = destination.with_suffix(".tmp.mp3")
    temporary.unlink(missing_ok=True)
    started = time.perf_counter()
    try:
        with client.audio.speech.with_streaming_response.create(
            model=MODEL,
            voice=voice,
            input=text,
            instructions=instructions,
        ) as response:
            response.stream_to_file(temporary)
        elapsed = time.perf_counter() - started
        temporary.replace(destination)
        return elapsed, destination.stat().st_size
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def build_table(voices, variants, lines, available_files):
    headings = "".join(f"<th>{html.escape(line)}</th>" for line in lines)
    rows = []
    for voice in voices:
        for variant in variants:
            cells = []
            for line in lines:
                filename = audio_filename(voice, variant, line)
                if filename in available_files:
                    escaped_filename = html.escape(filename, quote=True)
                    cells.append(
                        '<td><div class="clip-cell"><audio controls preload="none" src="'
                        + escaped_filename
                        + '"></audio><a class="download" href="'
                        + escaped_filename
                        + '" download="'
                        + escaped_filename
                        + '">Download MP3</a></div></td>'
                    )
                else:
                    cells.append('<td class="missing">Unavailable</td>')
            rows.append(
                f"<tr><th>{html.escape(voice)} × {html.escape(variant)}</th>"
                + "".join(cells)
                + "</tr>"
            )
    return (
        "<table><thead><tr><th>Voice × variant</th>"
        + headings
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def write_index(voices, variants, lines):
    available_files = {
        path.name
        for path in OUT_DIR.glob("*.mp3")
        if path.is_file() and path.stat().st_size > 0
    }
    clips = [
        {
            "file": filename,
            "voice": voice,
            "variant": variant,
            "line": line,
        }
        for voice in voices
        for variant in variants
        for line in lines
        if (filename := audio_filename(voice, variant, line)) in available_files
    ]
    table = build_table(voices, variants, lines, available_files)
    clips_json = json.dumps(clips, ensure_ascii=True).replace("</", "<\\/")
    page = HTML_TEMPLATE.replace("__TABLE__", table).replace("__CLIPS__", clips_json)
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a Salvatore voice × instructions TTS audition matrix."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="generate all seven lines (default: greeting and exclaim1)",
    )
    parser.add_argument(
        "--voices",
        help="comma-separated subset, e.g. cedar,fable",
    )
    parser.add_argument(
        "--variants",
        help="comma-separated subset, e.g. v0,v2",
    )
    parser.add_argument(
        "--lines",
        help="comma-separated line subset; overrides quick/full line selection",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite audio files that already exist",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="OpenAI request timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=1,
        help="OpenAI SDK retry count per clip (default: 1)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.timeout <= 0:
        raise SystemExit("--timeout must be greater than 0")
    if args.max_retries < 0:
        raise SystemExit("--max-retries must be 0 or greater")

    default_voices = VOICES if args.full else QUICK_VOICES
    voices = selected_values(args.voices, VOICES, "voices") if args.voices else list(default_voices)
    variants = selected_values(args.variants, VARIANTS, "variants")
    default_lines = TEST_LINES if args.full else QUICK_LINES
    lines = selected_values(args.lines, TEST_LINES, "lines") if args.lines else list(default_lines)

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Export it or create "
            "experiments/tts_audition/.env with OPENAI_API_KEY=sk-..."
        )
    try:
        print("Loading OpenAI SDK...", flush=True)
        from openai import OpenAI
    except ImportError:
        raise SystemExit(
            "The 'openai' package is required. Install the repository requirements first."
        ) from None

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    latency_path = OUT_DIR / "latency.csv"
    failures_path = OUT_DIR / "failures.csv"
    latencies = read_keyed_csv(latency_path, LATENCY_FIELDS)
    failures = read_keyed_csv(failures_path, FAILURE_FIELDS)
    client = OpenAI(api_key=api_key, timeout=args.timeout, max_retries=args.max_retries)

    total = len(voices) * len(variants) * len(lines)
    completed = skipped = failed = 0
    print(
        f"Generating {total} clips with {MODEL} "
        f"({len(voices)} voices × {len(variants)} variants × {len(lines)} lines); "
        f"timeout={args.timeout:g}s, max_retries={args.max_retries}",
        flush=True,
    )

    for voice in voices:
        for variant in variants:
            for line in lines:
                key = (voice, variant, line)
                destination = OUT_DIR / audio_filename(*key)
                label = f"[{completed + skipped + failed + 1}/{total}] {destination.name}"
                if destination.exists() and destination.stat().st_size > 0 and not args.force:
                    skipped += 1
                    if key not in latencies:
                        latencies[key] = {
                            "voice": voice,
                            "variant": variant,
                            "line": line,
                            "seconds": "",
                            "bytes": destination.stat().st_size,
                        }
                    print(f"{label} — exists, skipped", flush=True)
                    continue
                try:
                    print(f"{label} — START", flush=True)
                    seconds, byte_count = create_audio(
                        client,
                        voice,
                        VARIANTS[variant],
                        TEST_LINES[line],
                        destination,
                    )
                    latencies[key] = {
                        "voice": voice,
                        "variant": variant,
                        "line": line,
                        "seconds": f"{seconds:.3f}",
                        "bytes": byte_count,
                    }
                    failures.pop(key, None)
                    completed += 1
                    print(f"{label} — DONE {seconds:.2f}s, {byte_count:,} bytes", flush=True)
                except Exception as error:
                    failed += 1
                    message = str(error).replace("\n", " ").strip() or type(error).__name__
                    failures[key] = {
                        "voice": voice,
                        "variant": variant,
                        "line": line,
                        "error": message,
                    }
                    print(f"{label} — FAILED: {message}", file=sys.stderr, flush=True)

                # Persist progress so an interrupted full run remains usable.
                write_csv(latency_path, LATENCY_FIELDS, latencies)
                write_csv(failures_path, FAILURE_FIELDS, failures)

    write_csv(latency_path, LATENCY_FIELDS, latencies)
    write_csv(failures_path, FAILURE_FIELDS, failures)
    write_index(voices, variants, lines)
    print(
        f"Done: {completed} generated, {skipped} skipped, {failed} failed. "
        f"Open {OUT_DIR / 'index.html'}",
        flush=True,
    )
    if failed:
        print(f"Failure details: {failures_path}", file=sys.stderr, flush=True)


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Salvatore TTS Audition</title>
  <style>
    :root { color-scheme: light; font-family: ui-sans-serif, system-ui, sans-serif; }
    body { margin: 0; background: #f5f1e8; color: #28231d; }
    header { padding: 24px clamp(18px, 5vw, 64px); background: #423629; color: #fffaf0; }
    h1 { margin: 0 0 8px; font-family: Georgia, serif; }
    header p { margin: 0; color: #e7dcc8; }
    nav { display: flex; gap: 10px; padding: 18px clamp(18px, 5vw, 64px) 0; }
    button {
      border: 1px solid #846c4f; border-radius: 7px; background: #fffaf0;
      color: #423629; padding: 9px 14px; cursor: pointer; font-weight: 650;
    }
    button.active, button.primary { background: #765535; color: white; }
    button:disabled { cursor: not-allowed; opacity: .45; }
    main { padding: 18px clamp(18px, 5vw, 64px) 48px; }
    .hidden { display: none !important; }
    .table-wrap { overflow-x: auto; background: white; border-radius: 10px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd2c1; padding: 10px; text-align: left; }
    thead th { background: #ece2d2; position: sticky; top: 0; }
    tbody th { white-space: nowrap; background: #faf6ef; }
    audio { width: 230px; max-width: 28vw; }
    .clip-cell { display: flex; flex-direction: column; gap: 7px; }
    .download { color: #765535; font-weight: 650; text-decoration: none; }
    .download:hover { text-decoration: underline; }
    .missing { color: #8b8175; font-style: italic; text-align: center; }
    #blindCard {
      max-width: 660px; margin: 12px auto; padding: 28px; border-radius: 12px;
      background: white; box-shadow: 0 8px 30px #4d3d2820;
    }
    #blindAudio { width: 100%; max-width: none; margin: 18px 0; }
    .controls, .ratings { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 14px; }
    .ratings button.selected { background: #765535; color: white; }
    #saveStatus { min-height: 1.3em; margin-top: 8px; color: #71675b; }
    #identity { padding: 12px; margin-top: 16px; background: #f1e8d9; border-radius: 7px; }
    #empty { text-align: center; color: #71675b; }
    .hint { color: #71675b; font-size: .92rem; }
  </style>
</head>
<body>
  <header>
    <h1>Salvatore TTS Audition</h1>
    <p>Compare voices and instruction hypotheses, then score them blind.</p>
  </header>
  <nav>
    <button id="tableTab" class="active">Matrix</button>
    <button id="blindTab">Blind listening</button>
  </nav>
  <main>
    <section id="tableView">
      <div class="table-wrap">__TABLE__</div>
    </section>
    <section id="blindView" class="hidden">
      <div id="blindCard">
        <div id="empty" class="hidden">No generated clips are available.</div>
        <div id="player">
          <strong id="progress"></strong>
          <p class="hint">The identity stays hidden until the clip finishes and you reveal it.</p>
          <audio id="blindAudio" controls preload="auto"></audio>
          <div class="controls">
            <button id="reveal" disabled>Reveal identity</button>
            <button id="reshuffle">Reshuffle</button>
            <button id="export">Export ratings CSV</button>
          </div>
          <div id="identity" class="hidden"></div>
          <div class="ratings">
            <span>Score:</span>
            <button data-score="1">1</button><button data-score="2">2</button>
            <button data-score="3">3</button><button data-score="4">4</button>
            <button data-score="5">5</button>
          </div>
          <div class="controls"><button id="saveRating">Save rating</button></div>
          <div id="saveStatus" class="hint"></div>
          <div class="controls"><button id="next" class="primary">Next clip</button></div>
        </div>
      </div>
    </section>
  </main>
  <script>
    const clips = __CLIPS__;
    const storageKey = "salvatore-tts-audition-ratings-v1";
    let ratings;
    try { ratings = JSON.parse(localStorage.getItem(storageKey) || "{}"); }
    catch (_) { ratings = {}; }
    let queue = [];
    let position = 0;
    let heard = false;
    let selectedScore = null;

    const $ = (id) => document.getElementById(id);
    const shuffle = (items) => {
      const copy = [...items];
      for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }
      return copy;
    };
    const current = () => queue[position];
    const csvCell = (value) => '"' + String(value ?? "").replaceAll('"', '""') + '"';

    function switchView(blind) {
      $("tableView").classList.toggle("hidden", blind);
      $("blindView").classList.toggle("hidden", !blind);
      $("tableTab").classList.toggle("active", !blind);
      $("blindTab").classList.toggle("active", blind);
    }
    $("tableTab").onclick = () => switchView(false);
    $("blindTab").onclick = () => switchView(true);

    function renderClip() {
      if (!queue.length) {
        $("player").classList.add("hidden");
        $("empty").classList.remove("hidden");
        return;
      }
      heard = false;
      const clip = current();
      selectedScore = ratings[clip.file] || null;
      $("progress").textContent = `Clip ${position + 1} of ${queue.length}`;
      $("blindAudio").src = clip.file;
      $("reveal").disabled = true;
      $("identity").classList.add("hidden");
      $("identity").textContent = "";
      $("saveRating").disabled = selectedScore === null;
      $("saveStatus").textContent = selectedScore ? `Saved score: ${selectedScore}` : "No score saved yet.";
      document.querySelectorAll("[data-score]").forEach((button) => {
        button.classList.toggle("selected", Number(button.dataset.score) === selectedScore);
      });
    }

    $("blindAudio").addEventListener("ended", () => {
      heard = true;
      $("reveal").disabled = false;
    });
    $("reveal").onclick = () => {
      if (!heard) return;
      const clip = current();
      $("identity").textContent =
        `Voice: ${clip.voice} · Variant: ${clip.variant} · Line: ${clip.line}`;
      $("identity").classList.remove("hidden");
    };
    $("next").onclick = () => {
      position = (position + 1) % queue.length;
      renderClip();
    };
    $("reshuffle").onclick = () => {
      queue = shuffle(clips);
      position = 0;
      renderClip();
    };
    document.querySelectorAll("[data-score]").forEach((button) => {
      button.onclick = () => {
        selectedScore = Number(button.dataset.score);
        $("saveRating").disabled = false;
        $("saveStatus").textContent = "Unsaved score selected.";
        document.querySelectorAll("[data-score]").forEach((scoreButton) => {
          scoreButton.classList.toggle("selected", scoreButton === button);
        });
      };
    });
    $("saveRating").onclick = () => {
      const clip = current();
      if (!clip || selectedScore === null) return;
      ratings[clip.file] = selectedScore;
      localStorage.setItem(storageKey, JSON.stringify(ratings));
      $("saveStatus").textContent = `Saved score: ${selectedScore}`;
    };
    $("export").onclick = () => {
      const rows = [["voice", "variant", "line", "score", "file"]];
      clips.forEach((clip) => {
        if (ratings[clip.file]) {
          rows.push([clip.voice, clip.variant, clip.line, ratings[clip.file], clip.file]);
        }
      });
      const csv = rows.map((row) => row.map(csvCell).join(",")).join("\r\n");
      const url = URL.createObjectURL(new Blob([csv], {type: "text/csv;charset=utf-8"}));
      const link = document.createElement("a");
      link.href = url;
      link.download = "salvatore_tts_ratings.csv";
      link.click();
      URL.revokeObjectURL(url);
    };

    queue = shuffle(clips);
    renderClip();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
