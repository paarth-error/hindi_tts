"""
04_transcribe_whisper.py
------------------------
Whisper large-v3 se har diarized audio chunk ka Devanagari Hindi
transcription karo aur ek master metadata.csv banao.

Reads  : data/03_diarized_segments/**/*.wav
Writes : data/04_transcripts/**/*.txt  (per-chunk transcripts)
         data/metadata.csv             (master dataset file)

metadata.csv format:
    audio_path | speaker_id | language | text

Usage:
    python3 scripts/04_transcribe_whisper.py

Dependencies:
    pip3 install openai-whisper pandas torch
"""

import glob
import os

import pandas as pd
import torch
import whisper

# ── Folder paths ──────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SEGMENTS_DIR  = os.path.join(BASE_DIR, "..", "data", "03_diarized_segments")
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "..", "data", "04_transcripts")
METADATA_PATH = os.path.join(BASE_DIR, "..", "data", "metadata.csv")

os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

# ── Model config ──────────────────────────────────────────────────────────────
# "large-v3" = best accuracy. Use "medium" or "small" for faster testing.
WHISPER_MODEL = "medium"
LANGUAGE      = "hi"   # Hindi → Devanagari output


def get_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    # Apple Silicon MPS — faster than CPU on M1/M2/M3
    # Note: Whisper has some MPS limitations, CPU is more stable
    return "cpu"


def transcribe_chunks() -> None:
    wav_files = sorted(glob.glob(
        os.path.join(SEGMENTS_DIR, "**", "*.wav"), recursive=True
    ))

    if not wav_files:
        print(f"[-] Koi .wav chunks nahi mile: {os.path.abspath(SEGMENTS_DIR)}")
        print("    Pehle 03_diarize_pyannote.py run karo.")
        return

    print(f"[*] {len(wav_files)} audio chunks mile transcribe karne ke liye.\n")

    # ── Load Whisper model ────────────────────────────────────────────────────
    device = get_device()
    print(f"[*] Whisper '{WHISPER_MODEL}' load ho raha hai on {device.upper()}...")
    print("    (Pehli baar ~3GB model download hoga — wait karo)\n")
    model = whisper.load_model(WHISPER_MODEL, device=device)
    print("[+] Model ready!\n")

    dataset_records = []
    total = len(wav_files)

    for idx, wav_path in enumerate(wav_files, start=1):
        try:
            # Speaker ID folder structure se nikalo
            # e.g. .../03_diarized_segments/story_name/SPEAKER_00/chunk.wav
            path_parts = wav_path.replace("\\", "/").split("/")
            speaker_id = path_parts[-2]   # SPEAKER_00
            story_name = path_parts[-3]   # story folder name

            result = model.transcribe(
                wav_path,
                language=LANGUAGE,
                task="transcribe",
                fp16=False,   # fp16 only for CUDA; MPS/CPU ke liye False
            )

            text = result["text"].strip()

            if not text:
                continue  # empty result skip karo

            # Per-chunk .txt file save karo
            relative_path = os.path.relpath(wav_path, SEGMENTS_DIR)
            txt_out = os.path.join(
                TRANSCRIPTS_DIR,
                os.path.splitext(relative_path)[0] + ".txt"
            )
            os.makedirs(os.path.dirname(txt_out), exist_ok=True)
            with open(txt_out, "w", encoding="utf-8") as f:
                f.write(text)

            dataset_records.append({
                "audio_path": wav_path,
                "speaker_id": speaker_id,
                "story":      story_name,
                "language":   LANGUAGE,
                "text":       text,
            })

            print(f"[{idx}/{total}] [{speaker_id}] {text}")

        except Exception as e:
            print(f"[-] Error on {os.path.basename(wav_path)}: {e}")

    # ── Save master metadata.csv ──────────────────────────────────────────────
    if dataset_records:
        df = pd.DataFrame(dataset_records)
        df.to_csv(METADATA_PATH, index=False, encoding="utf-8-sig")
        print(f"\n[+] Done! {len(dataset_records)} segments transcribed.")
        print(f"[+] Master CSV saved: {os.path.abspath(METADATA_PATH)}")
    else:
        print("\n[-] Koi transcript nahi bana — audio files check karo.")


if __name__ == "__main__":
    transcribe_chunks()
