#!/usr/bin/env python3
"""Standalone Coqui XTTS v2 smoke test for Salvatore Italian-accent English refs."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import torch


def pick_device(requested: str) -> str:
    if requested != "auto":
        return requested
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    default_refs = sorted((repo / "voices" / "salvatore").glob("salvatore_ref_*.wav"))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refs",
        nargs="+",
        default=[str(p) for p in default_refs],
        help="Reference WAV paths for voice cloning",
    )
    parser.add_argument(
        "--text",
        default="Hello, I'm Celeste. How are you today? Let's explore the room together.",
    )
    parser.add_argument("--language", default="en")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "mps"])
    parser.add_argument(
        "--out-dir",
        default=str(repo / "tmp_xtts_out"),
    )
    args = parser.parse_args()

    os.environ.setdefault("COQUI_TOS_AGREED", "1")
    # Helpful when MPS hits unsupported ops.
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

    refs = [Path(p).expanduser().resolve() for p in args.refs]
    missing = [str(p) for p in refs if not p.is_file()]
    if missing:
        raise SystemExit(f"Missing reference files: {missing}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    device = pick_device(args.device)
    print(f"device={device}")
    print(f"refs={[p.name for p in refs]}")
    print(f"text={args.text!r}")

    from TTS.api import TTS

    t_load0 = time.perf_counter()
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    tts = tts.to(device)
    print(f"model_load_s={time.perf_counter() - t_load0:.2f}")

    wav_path = out_dir / f"salvatore_{device}.wav"
    mp3_path = out_dir / f"salvatore_{device}.mp3"

    t0 = time.perf_counter()
    tts.tts_to_file(
        text=args.text,
        speaker_wav=[str(p) for p in refs],
        language=args.language,
        file_path=str(wav_path),
        split_sentences=True,
    )
    synth_s = time.perf_counter() - t0
    print(f"synth_s={synth_s:.2f}")
    print(f"wrote {wav_path} ({wav_path.stat().st_size} bytes)")

    # Convert to MP3 for robot playback path parity.
    from pydub import AudioSegment

    AudioSegment.from_wav(str(wav_path)).export(str(mp3_path), format="mp3")
    print(f"wrote {mp3_path} ({mp3_path.stat().st_size} bytes)")
    print("done")


if __name__ == "__main__":
    main()
