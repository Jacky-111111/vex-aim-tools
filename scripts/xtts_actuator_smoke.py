#!/usr/bin/env python3
"""Smoke-test SoundActuator.synthesize_xtts without a physical robot."""

from __future__ import annotations

import os
import sys
import time
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

os.environ.setdefault("COQUI_TOS_AGREED", "1")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")


def _install_stubs() -> None:
    # Import torch/TTS first so inspect-based imports are not polluted by stubs.
    import torch  # noqa: F401
    from TTS.api import TTS  # noqa: F401

    vex = types.ModuleType("vex")
    vex.__file__ = "<vex-stub>"
    vex.aim = types.SimpleNamespace(InvalidSoundFileException=Exception)
    vex.EmojiType = types.SimpleNamespace()
    vex.EmojiLookType = types.SimpleNamespace(LOOK_FORWARD="LOOK_FORWARD")
    sys.modules["vex"] = vex

    google = types.ModuleType("google")
    google.__file__ = "<google-stub>"
    cloud = types.ModuleType("google.cloud")
    cloud.__file__ = "<google.cloud-stub>"
    tts = types.ModuleType("google.cloud.texttospeech")
    tts.__file__ = "<google.cloud.texttospeech-stub>"
    tts.TextToSpeechClient = object
    tts.VoiceSelectionParams = object
    tts.AudioConfig = object
    tts.AudioEncoding = types.SimpleNamespace(MP3="MP3")
    tts.SsmlVoiceGender = types.SimpleNamespace(FEMALE="FEMALE")
    tts.SynthesisInput = object
    cloud.texttospeech = tts
    cloud.api_credentials = None
    google.cloud = cloud
    sys.modules["google"] = google
    sys.modules["google.cloud"] = cloud
    sys.modules["google.cloud.texttospeech"] = tts

    gtts = types.ModuleType("gtts")
    gtts.__file__ = "<gtts-stub>"
    gtts.gTTS = object
    sys.modules["gtts"] = gtts

    pkg = types.ModuleType("aim_fsm")
    pkg.__file__ = str(REPO / "aim_fsm" / "__init__.py")
    pkg.__path__ = [str(REPO / "aim_fsm")]
    sys.modules["aim_fsm"] = pkg

    geom = types.ModuleType("aim_fsm.geometry")
    geom.__file__ = str(REPO / "aim_fsm" / "geometry.py")
    geom.wrap_angle = lambda x: x
    sys.modules["aim_fsm.geometry"] = geom


def main() -> None:
    _install_stubs()
    from aim_fsm.actuators import SoundActuator

    out = REPO / "tmp_xtts_out" / "actuator_smoke.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)

    robot = types.SimpleNamespace(openai_client=None)
    sound = SoundActuator.__new__(SoundActuator)
    sound.robot = robot
    sound.xtts_tts = None
    sound.xtts_device = None
    sound.tts_client = None

    params = {
        "speaker_wav": [
            "voices/salvatore/salvatore_ref_a.wav",
            "voices/salvatore/salvatore_ref_b.wav",
            "voices/salvatore/salvatore_ref_c.wav",
        ],
        "language": "en",
        "device": "cpu",
    }
    text = "Hello, I'm Celeste. This is the XTTS actuator smoke test."
    t0 = time.perf_counter()
    sound.synthesize_xtts(text, str(out), None, params)
    print(f"ok wrote {out} in {time.perf_counter() - t0:.2f}s ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
