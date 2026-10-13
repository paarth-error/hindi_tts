"""
02_separate_audio.py
--------------------
BGM hatao, clean "dry vocals" nikalo.

Reads  : data/01_raw_audio/*.wav
Writes : data/02_isolated_vocals/<filename>_dry_vocal.wav

Uses Demucs htdemucs model (--two-stem=vocals) to separate background
music from speech. GPU pe fast chalega; CPU par thoda time lagega.

Usage:
    python scripts/02_separate_audio.py

Dependencies:
    demucs  (pip install demucs)
    ffmpeg  (system install — brew install ffmpeg)
"""

import glob
import os
import shutil
import subprocess

# ── Folder paths (relative to this script's location) ────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
RAW_DIR    = os.path.join(BASE_DIR, "..", "data", "01_raw_audio")
VOCALS_DIR = os.path.join(BASE_DIR, "..", "data", "02_isolated_vocals")
TEMP_OUT   = os.path.join(BASE_DIR, "..", "data", "temp_demucs")

os.makedirs(VOCALS_DIR, exist_ok=True)


def isolate_clean_vocals() -> None:
    wav_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.wav")))

    if not wav_files:
        print(f"[-] Koi .wav file nahi mili: {os.path.abspath(RAW_DIR)}")
        print("    Pehle 01_scrape_youtube.py run karo.")
        return

    print(f"[*] {len(wav_files)} file(s) mili — vocal isolation shuru karte hain...\n")

    for wav_path in wav_files:
        filename  = os.path.basename(wav_path)
        raw_name  = os.path.splitext(filename)[0]

        print(f"[*] Demucs processing: {filename}")

        # Skip if already processed
        final_path = os.path.join(VOCALS_DIR, f"{raw_name}_dry_vocal.wav")
        if os.path.exists(final_path):
            print(f"[~] Already processed, skipping: {filename}\n")
            continue

        # demucs CLI:
        #   --two-stem vocals  → sirf vocals + no_vocals stems banao
        #   -n htdemucs        → Hybrid Transformer model (best quality)
        #   -o TEMP_OUT        → temp output folder
        cmd = [
            "demucs",
            "--two-stem", "vocals",
            "-n", "htdemucs",
            "-o", TEMP_OUT,
            wav_path,
        ]

        try:
            subprocess.run(cmd, check=True)

            # Demucs output path: TEMP_OUT/htdemucs/<raw_name>/vocals.wav
            extracted_vocal = os.path.join(TEMP_OUT, "htdemucs", raw_name, "vocals.wav")

            if os.path.exists(extracted_vocal):
                final_path = os.path.join(VOCALS_DIR, f"{raw_name}_dry_vocal.wav")
                shutil.move(extracted_vocal, final_path)
                print(f"[+] Clean vocal saved: {os.path.abspath(final_path)}\n")
            else:
                print(f"[-] vocals.wav nahi mili expected path par: {extracted_vocal}\n")

        except subprocess.CalledProcessError as e:
            print(f"[-] Demucs error on '{filename}': {e}\n")
        except Exception as e:
            print(f"[-] Unexpected error on '{filename}': {e}\n")

    # Temp folder cleanup
    if os.path.exists(TEMP_OUT):
        shutil.rmtree(TEMP_OUT)
        print("[*] Temp folder cleaned up.")

    print("\n[+] Vocal isolation complete!")
    print(f"    Output folder: {os.path.abspath(VOCALS_DIR)}")


if __name__ == "__main__":
    isolate_clean_vocals()
