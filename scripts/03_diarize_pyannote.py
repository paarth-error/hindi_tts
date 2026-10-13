"""
03_diarize_pyannote.py
----------------------
Speaker diarization using Pyannote 3.1.

Reads  : data/02_isolated_vocals/*_dry_vocal.wav
Writes : data/03_diarized_segments/<base_name>/<SPEAKER_XX>/<chunk>.wav

Each audio file is split into per-speaker chunks (min 2 seconds).
Useful for separating narrator vs characters in Hindi audiobooks.

Usage:
    python scripts/03_diarize_pyannote.py

Setup:
    1. pip install pyannote.audio pydub torch
    2. Accept model terms on HuggingFace:
       - https://huggingface.co/pyannote/speaker-diarization-3.1
       - https://huggingface.co/pyannote/segmentation-3.0
    3. Set HF_TOKEN in a .env file (see .env.example)
"""

import glob
import os

# ── Force soundfile backend before importing pyannote ────────────────────────
# torchcodec fails on Python 3.14 + Homebrew FFmpeg 9 (missing LC_RPATH)
os.environ["TORCHAUDIO_USE_BACKEND_DISPATCHER"] = "1"

import numpy as np
import soundfile as sf
import torch
import torchaudio
from dotenv import load_dotenv
from pyannote.audio import Pipeline

# ── Load token from .env ──────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
HF_TOKEN = os.environ.get("HF_TOKEN")

if not HF_TOKEN:
    raise EnvironmentError(
        "HF_TOKEN not set.\n"
        "Apne .env file mein HF_TOKEN=hf_xxxx daalo (project root mein)."
    )

# ── Folder paths ──────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
VOCALS_DIR   = os.path.join(BASE_DIR, "..", "data", "02_isolated_vocals")
SEGMENTS_DIR = os.path.join(BASE_DIR, "..", "data", "03_diarized_segments")

os.makedirs(SEGMENTS_DIR, exist_ok=True)

# Minimum segment duration to keep (seconds)
MIN_DURATION_SEC = 2.0


def run_speaker_diarization() -> None:
    vocal_files = sorted(glob.glob(os.path.join(VOCALS_DIR, "*_dry_vocal.wav")))

    if not vocal_files:
        print(f"[-] Koi dry vocal file nahi mili: {os.path.abspath(VOCALS_DIR)}")
        print("    Pehle 02_separate_audio.py run karo.")
        return

    # ── Load Pyannote pipeline ────────────────────────────────────────────────
    print("[*] Pyannote 3.1 pipeline load ho raha hai (pehli baar model download hoga)...")
    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=HF_TOKEN,
        )
    except Exception as e:
        print(f"[-] Pipeline load failed: {e}")
        print("    HF_TOKEN aur model access permissions check karo.")
        return

    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
        print("[+] CUDA GPU enabled.\n")
    elif torch.backends.mps.is_available():
        pipeline.to(torch.device("mps"))
        print("[+] Apple Silicon MPS enabled.\n")
    else:
        print("[!] CPU par chal raha hai (slow ho sakta hai).\n")

    # ── Process each vocal file ───────────────────────────────────────────────
    for audio_path in vocal_files:
        filename  = os.path.basename(audio_path)
        base_name = filename.replace("_dry_vocal.wav", "")

        print(f"[*] Diarizing: {filename} ...")

        try:
            # Load audio via soundfile (bypasses torchcodec entirely)
            audio_data, sample_rate = sf.read(audio_path)
            if audio_data.ndim > 1:
                audio_data = audio_data.mean(axis=1)
            # Convert to torch tensor — pyannote accepts {"waveform": tensor, "sample_rate": int}
            waveform = torch.tensor(audio_data, dtype=torch.float32).unsqueeze(0)
            diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate})
        except Exception as e:
            print(f"[-] Diarization failed on '{filename}': {e}\n")
            continue

        # audio_data + sample_rate already loaded above

        segment_count = 0

        for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):
            duration_sec = turn.end - turn.start

            # Skip very short clips — too noisy for TTS training
            if duration_sec < MIN_DURATION_SEC:
                continue

            start_sample = int(turn.start * sample_rate)
            end_sample   = int(turn.end   * sample_rate)

            # Per-speaker subfolder: 03_diarized_segments/<base_name>/SPEAKER_00/
            speaker_dir = os.path.join(SEGMENTS_DIR, base_name, speaker)
            os.makedirs(speaker_dir, exist_ok=True)

            chunk      = audio_data[start_sample:end_sample]
            chunk_name = f"{speaker}_{segment_count:04d}_{int(turn.start)}s.wav"
            chunk_path = os.path.join(speaker_dir, chunk_name)

            sf.write(chunk_path, chunk, sample_rate)
            segment_count += 1

        print(f"[+] {segment_count} segments saved for: {base_name}\n")

    print("[+] Speaker diarization complete!")
    print(f"    Output: {os.path.abspath(SEGMENTS_DIR)}")


if __name__ == "__main__":
    run_speaker_diarization()
