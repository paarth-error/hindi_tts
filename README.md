# Hindi TTS Dataset Pipeline

End-to-end pipeline for building a clean Hindi speech dataset suitable for TTS model training.  
Downloads audio from YouTube → isolates vocals → diarizes speakers → transcribes in Devanagari.

---

## Folder Structure

```
hindi_tts_dataset/
├── data/
│   ├── 01_raw_audio/          # Direct YouTube downloads (WAV)
│   ├── 02_isolated_vocals/    # Demucs output (voice without BGM)
│   ├── 03_diarized_segments/  # Pyannote chunks (Speaker A, B …)
│   └── 04_transcripts/        # Whisper-v3 Devanagari transcripts
├── scripts/
│   ├── 01_scrape_youtube.py
│   ├── 02_separate_audio.py
│   ├── 03_diarize_pyannote.py
│   └── 04_transcribe_whisper.py
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Prerequisites

- Python 3.10+
- `ffmpeg` installed and on your PATH (`brew install ffmpeg` on macOS)
- A HuggingFace account with access to [`pyannote/speaker-diarization-3.1`](https://huggingface.co/pyannote/speaker-diarization-3.1)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your HuggingFace token

```bash
export HF_TOKEN="hf_your_token_here"
```

---

## Pipeline Steps

### Step 1 — Download audio from YouTube

```bash
# Single URL
python scripts/01_scrape_youtube.py --url "https://youtu.be/VIDEO_ID"

# Batch (one URL per line in urls.txt)
python scripts/01_scrape_youtube.py --urls urls.txt
```

Output: `data/01_raw_audio/*.wav`

---

### Step 2 — Separate vocals from background music

```bash
python scripts/02_separate_audio.py
```

Uses [Demucs](https://github.com/facebookresearch/demucs) (`htdemucs` model, two-stem split).  
Output: `data/02_isolated_vocals/`

---

### Step 3 — Speaker diarization

```bash
python scripts/03_diarize_pyannote.py
```

Uses [Pyannote.audio 3.1](https://github.com/pyannote/pyannote-audio).  
Splits audio into per-speaker WAV chunks.  
Output: `data/03_diarized_segments/<source_name>/<SPEAKER_XX_start_end>.wav`

---

### Step 4 — Transcribe to Devanagari

```bash
python scripts/04_transcribe_whisper.py
```

Uses [Whisper large-v3](https://github.com/openai/whisper) with `language=hi`.  
Writes one `.txt` per segment and a combined `transcripts_manifest.jsonl`.  
Output: `data/04_transcripts/`

---

## Notes

- GPU strongly recommended for steps 3 and 4. The scripts auto-detect CUDA.
- Whisper `task="transcribe"` keeps Hindi output in Devanagari. Change to `"translate"` for English.
- The `data/` directories are git-tracked via `.gitkeep` but their contents are intended to be in `.gitignore`.
