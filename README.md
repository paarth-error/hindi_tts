# 🎤 Hindi TTS Dataset Creation & Training Pipeline

A complete pipeline to create and train high-quality Hindi Text-to-Speech models from YouTube videos.

## 🌟 Features

- ✅ **Automated data collection** from YouTube
- ✅ **Professional audio processing** (vocal separation, speaker diarization)
- ✅ **AI-powered transcription** using Whisper
- ✅ **LLM metadata tagging** for better quality control
- ✅ **Multiple training framework support** (GPT-SoVITS, XTTS, Piper)
- ✅ **Optimized for Mac M1/M2/M3 and NVIDIA GPUs**

## 📋 Pipeline Overview

```
YouTube Videos
    ↓
1. Scrape & Download (yt-dlp)
    ↓
2. Separate Vocals (Demucs)
    ↓
3. Diarize Speakers (Pyannote 3.1)
    ↓
4. Transcribe Audio (Whisper Large v3)
    ↓
5. LLM Tagging (Groq API)
    ↓
6. Export Manifest
    ↓
7. Format for Training (GPT-SoVITS/XTTS/Piper)
    ↓
8. Train TTS Model
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Python 3.14 supported with workarounds)
- **GPU:** NVIDIA (CUDA) or Apple Silicon (M1/M2/M3)
- **Disk Space:** 20GB+ free
- **FFmpeg** installed
- **API Keys:**
  - HuggingFace token (for Pyannote)
  - Groq API key (for LLM tagging)

### Installation

```bash
# Clone repository
git clone https://github.com/paarth-error/hindi_tts.git
cd hindi_tts/hindi_tts_dataset

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your HF_TOKEN and GROQ_API_KEY
```

### Usage

#### Option 1: Run All Steps Sequentially

```bash
# Step 1: Download YouTube videos (16 already downloaded)
python3 scripts/01_scrape_youtube.py

# Step 2: Separate vocals from background music
python3 scripts/02_separate_audio.py

# Step 3: Separate different speakers
python3 scripts/03_diarize_pyannote.py

# Step 4: Transcribe audio to text
python3 scripts/04_transcribe_whisper.py

# Step 5: Add LLM metadata (optional)
python3 scripts/05_llm_tag_groq.py

# Step 6: Export training manifest
python3 scripts/06_export_manifest.py

# Step 7: Check dataset statistics
python3 scripts/08_format_sovits.py --stats
```

#### Option 2: Use Kiro AI Assistant

For automated setup with Kiro IDE:

**📋 Copy-paste this into Kiro:**
> See `KIRO_PROMPT_FOR_TRAINING.md` for the complete prompt

## 🎯 Training

### GPT-SoVITS (Recommended - Best Quality)

```bash
# Install GPT-SoVITS
cd ..
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
pip install -r requirements.txt

# Prepare dataset
cd ../hindi_tts_dataset
python3 scripts/09_train_gpt_sovits_mac.py

# Start training (Web UI)
cd ../GPT-SoVITS
python3 webui.py
# Open browser: http://localhost:9874
```

### Coqui XTTS (Open Source Alternative)

```bash
pip install TTS
python3 scripts/08_format_sovits.py --format xtts
tts-train --config_path data/07_final/xtts_config.json
```

📖 **See `TRAINING_GUIDE.md` for detailed training instructions.**

## 📊 Dataset Statistics (Current)

- **Videos Downloaded:** 16 (20-30 more in background)
- **Raw Audio:** ~2-3 hours
- **Expected Final Samples:** 500-2000 clips
- **Speakers:** 2-3 distinct voices
- **Average Clip Length:** 3-8 seconds

## 🔧 Project Structure

```
hindi_tts_dataset/
├── data/
│   ├── 01_raw_audio/          # Downloaded audio files
│   ├── 02_isolated_vocals/    # Vocals only (no music)
│   ├── 03_diarized_segments/  # Speaker-separated clips
│   ├── 04_transcribed/        # Transcription JSONs
│   ├── 05_llm_tagged/         # LLM-tagged metadata
│   ├── 06_chunked/            # Final audio chunks
│   └── 07_final/              # Training manifest
├── scripts/
│   ├── 01_scrape_youtube.py
│   ├── 02_separate_audio.py
│   ├── 03_diarize_pyannote.py
│   ├── 04_transcribe_whisper.py
│   ├── 05_llm_tag_groq.py
│   ├── 06_export_manifest.py
│   ├── 08_format_sovits.py
│   └── 09_train_gpt_sovits_mac.py
├── requirements.txt
├── TRAINING_GUIDE.md              # Detailed training guide
├── KIRO_PROMPT_FOR_TRAINING.md    # Prompt for Kiro AI
└── README.md
```

## 🎤 Models Used

| Component | Model | Purpose |
|-----------|-------|---------|
| **Vocal Separation** | Demucs `htdemucs` | Remove background music |
| **Speaker Diarization** | Pyannote 3.1 | Separate speakers |
| **Transcription** | Whisper Large v3 | Speech-to-text |
| **LLM Tagging** | Groq `gpt-oss-20b` | Metadata generation |
| **TTS Training** | GPT-SoVITS / XTTS | Text-to-Speech |

## 💻 Hardware Requirements

### Minimum
- 8GB RAM
- 4GB GPU VRAM or Apple M1
- 20GB disk space

### Recommended
- 16GB RAM
- 8GB+ GPU VRAM or Apple M2/M3
- 50GB disk space (for training)

### Training Times (100 epochs)

| Hardware | Time |
|----------|------|
| **Mac M1 8GB** | 4-6 hours |
| **Mac M1 16GB** | 2-3 hours |
| **RTX 3060 12GB** | 1-2 hours |
| **RTX 4090 24GB** | 30-45 min |

## 🐛 Troubleshooting

### Python 3.14 Compatibility Issues
- Uses `soundfile` instead of `pydub`
- `torchaudio` backend configuration included
- All issues resolved in current scripts

### Pyannote 403 Error
1. Accept model terms: https://huggingface.co/pyannote/speaker-diarization-3.1
2. Get HF token: https://huggingface.co/settings/tokens
3. Add to `.env` file

### YouTube 403 on Cloud
- Works on Mac local IP
- Doesn't work on Colab/Kaggle IPs
- Use cookies.txt file for authentication

### Out of Memory
- Reduce batch size in training config
- Close other applications
- Use CPU training (slower)

## 📚 Documentation

- **[TRAINING_GUIDE.md](TRAINING_GUIDE.md)** - Complete training guide with 3 options
- **[KIRO_PROMPT_FOR_TRAINING.md](KIRO_PROMPT_FOR_TRAINING.md)** - AI assistant prompt for automated setup

## 🔐 Security Notes

- ⚠️ **Never commit `.env` file** (contains API keys)
- ✅ Use `.env.example` as template
- ✅ Regenerate tokens if accidentally exposed
- ✅ Add `.env` to `.gitignore` (already done)

## 🤝 Contributing

Issues and PRs welcome! This is an active project.

## 📝 License

MIT

## 🙏 Acknowledgments

- **Demucs** - Meta AI
- **Pyannote** - CNRS
- **Whisper** - OpenAI
- **GPT-SoVITS** - RVC-Boss
- **Groq** - Fast LLM inference

---

**Made with ❤️ for the Hindi TTS community**

For questions or issues: https://github.com/paarth-error/hindi_tts/issues
