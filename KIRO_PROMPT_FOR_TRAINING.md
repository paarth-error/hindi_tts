# 🎤 Kiro Prompt for Hindi TTS Training

Copy-paste this entire prompt into your Kiro IDE to set up and train the Hindi TTS model.

---

## 📋 Task for Kiro

I need to train a Hindi Text-to-Speech (TTS) model using a pre-processed dataset. The repository is already set up with all scripts and data processing complete. I need you to:

1. **Clone the repository** and verify all files
2. **Check system requirements** (GPU, disk space, Python version)
3. **Install GPT-SoVITS** (the TTS training framework)
4. **Prepare the dataset** for training
5. **Start training** with optimal settings for my hardware
6. **Monitor training** and provide checkpoints

---

## 🔗 Repository Information

**GitHub:** `https://github.com/paarth-error/hindi_tts.git`

**Project Structure:**
```
hindi_tts_dataset/
├── data/
│   ├── 01_raw_audio/           # Original downloaded audio
│   ├── 02_isolated_vocals/     # Vocals separated from music
│   ├── 03_diarized_segments/   # Speaker-separated audio chunks
│   ├── 04_transcribed/         # Transcriptions (to be generated)
│   ├── 05_llm_tagged/          # LLM-tagged metadata (to be generated)
│   ├── 06_chunked/             # Final chunked audio (to be generated)
│   └── 07_final/               # Training-ready manifest (to be generated)
├── scripts/
│   ├── 01_scrape_youtube.py    # ✅ Already run (16 videos downloaded)
│   ├── 02_separate_audio.py    # Step 2: Vocal separation
│   ├── 03_diarize_pyannote.py  # Step 3: Speaker diarization
│   ├── 04_transcribe_whisper.py # Step 4: Transcription
│   ├── 05_llm_tag_groq.py      # Step 5: LLM tagging
│   ├── 06_export_manifest.py   # Step 6: Export manifest
│   ├── 08_format_sovits.py     # Step 7: Format for training
│   └── 09_train_gpt_sovits_mac.py # Training setup
├── TRAINING_GUIDE.md           # Detailed training guide
├── requirements.txt            # Python dependencies
└── .env.example                # Environment variables template

```

---

## 🚀 Step-by-Step Instructions

### Step 1: Clone Repository
```bash
git clone https://github.com/paarth-error/hindi_tts.git
cd hindi_tts/hindi_tts_dataset
```

### Step 2: Check System Requirements

**Verify these before proceeding:**
- [ ] **Python 3.10+** (check with `python3 --version`)
- [ ] **CUDA GPU** (NVIDIA) or **Apple Silicon M1/M2/M3** (check with `nvidia-smi` or `system_profiler SPHardwareDataType`)
- [ ] **At least 20GB free disk space** (check with `df -h`)
- [ ] **At least 8GB RAM** (16GB recommended)

**If using Windows with NVIDIA GPU:**
- CUDA Toolkit 11.8 or 12.1 installed
- cuDNN installed

**If using Mac with Apple Silicon:**
- M1/M2/M3 chip
- macOS 12.3+ (for MPS support)

### Step 3: Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

```bash
# Copy example .env file
cp .env.example .env

# Edit .env and add your API keys
# HF_TOKEN: Get from https://huggingface.co/settings/tokens
# GROQ_API_KEY: Get from https://console.groq.com/keys
```

**Important:** Open `.env` file and add:
```
HF_TOKEN=your_huggingface_token_here
GROQ_API_KEY=your_groq_api_key_here
```

### Step 5: Run Data Processing Pipeline (Steps 2-7)

**Note:** Step 1 (YouTube scraping) is already complete with 16 videos downloaded.

```bash
# Step 2: Separate vocals from music using Demucs
python3 scripts/02_separate_audio.py

# Step 3: Diarize speakers using Pyannote
python3 scripts/03_diarize_pyannote.py

# Step 4: Transcribe audio using Whisper
python3 scripts/04_transcribe_whisper.py

# Step 5: Tag with LLM metadata
python3 scripts/05_llm_tag_groq.py

# Step 6: Export final manifest
python3 scripts/06_export_manifest.py

# Step 7: Format for GPT-SoVITS training
python3 scripts/08_format_sovits.py --format sovits
```

**Estimated Time:** 2-4 hours total (depending on GPU)

### Step 6: Install GPT-SoVITS

```bash
# Go to parent directory
cd ..

# Clone GPT-SoVITS
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS

# Install dependencies
pip install -r requirements.txt
```

### Step 7: Prepare Dataset for Training

```bash
cd ../hindi_tts_dataset
python3 scripts/09_train_gpt_sovits_mac.py
```

This will:
- Convert audio to 32kHz mono WAV format
- Filter samples by duration (2-15 seconds)
- Create training list file
- Generate training configuration

### Step 8: Start Training

**Option A: Using Web UI (Recommended - Easiest)**
```bash
cd ../GPT-SoVITS
python3 webui.py
```

Then:
1. Open browser: `http://localhost:9874`
2. Navigate to "Training" tab
3. Select dataset: `dataset/hindi_tts/`
4. Click "Start Training"
5. Monitor progress in real-time

**Option B: Using Command Line**
```bash
cd ../GPT-SoVITS
python3 GPT_SoVITS/s1_train.py \
  --config_path ../hindi_tts_dataset/data/07_final/config.json \
  --model_name hindi_tts \
  --device cuda  # Use 'mps' for Mac, 'cuda' for NVIDIA GPU
```

### Step 9: Monitor Training

**Watch for:**
- Loss values decreasing steadily
- Checkpoints saved every 500 steps
- Training time: ~2-3 hours for 100 epochs

**Check logs:**
```bash
tail -f GPT-SoVITS/logs/latest.log
```

### Step 10: Test the Trained Model

After training completes:

```python
# Test inference
cd GPT-SoVITS
python3 inference.py \
  --checkpoint logs/hindi_tts/best_checkpoint.pth \
  --text "नमस्ते, यह एक टेस्ट है।" \
  --output test_output.wav
```

---

## 🎯 Expected Results

**Dataset Statistics (after Step 6):**
- Total samples: ~500-2000 (depends on diarization)
- Total duration: ~1-3 hours of audio
- Speakers: 2-3 distinct voices
- Average clip length: 3-8 seconds

**Training Metrics:**
- Epoch 1: Loss ~15-20
- Epoch 50: Loss ~2-5
- Epoch 100: Loss ~0.5-1.5
- Best results: Usually around epoch 70-90

**Final Model:**
- Size: ~200-500MB
- Inference speed: 1-2 seconds for 5-second audio
- Quality: Near-human for single speaker

---

## 🔧 Troubleshooting

### "Out of Memory" Error
```bash
# Reduce batch size in config.json
# Change "batch_size": 8 to "batch_size": 4 or 2
```

### "CUDA out of memory"
```bash
# Close other applications
# Use smaller batch size
# Or use CPU (slower): --device cpu
```

### "HuggingFace 403 Error"
```bash
# Make sure you've:
# 1. Accepted Pyannote model terms: https://huggingface.co/pyannote/speaker-diarization-3.1
# 2. Added valid HF_TOKEN to .env file
```

### "Groq API Rate Limit"
```bash
# Step 5 (LLM tagging) is optional
# You can skip it and still train the model
# Or wait and retry after rate limit resets
```

### "Disk space full"
```bash
# Clear pip cache: pip cache purge
# Remove unused virtual environments
# Clean system temp files
```

---

## 📊 Hardware Recommendations

| Hardware | Batch Size | Training Time | Quality |
|----------|-----------|---------------|---------|
| **Mac M1 8GB** | 4 | 4-6 hours | Good |
| **Mac M1 16GB** | 8 | 2-3 hours | Good |
| **RTX 3060 12GB** | 16 | 1-2 hours | Excellent |
| **RTX 4090 24GB** | 32 | 30-45 min | Excellent |
| **CPU Only** | 2 | 12-24 hours | Good (slow) |

---

## 📖 Additional Resources

- **TRAINING_GUIDE.md** - Detailed training options (GPT-SoVITS, XTTS, Piper)
- **GPT-SoVITS Docs:** https://github.com/RVC-Boss/GPT-SoVITS
- **Pyannote Docs:** https://github.com/pyannote/pyannote-audio
- **Whisper Docs:** https://github.com/openai/whisper

---

## 💡 Pro Tips

1. **Keep laptop plugged in** during training (especially Mac)
2. **Close heavy applications** (Chrome, Docker, etc.) to free RAM
3. **Enable caffeinate** on Mac to prevent sleep:
   ```bash
   caffeinate -disu &
   ```
4. **Monitor GPU temperature:**
   ```bash
   # NVIDIA: watch -n 1 nvidia-smi
   # Mac: sudo powermetrics --samplers smc | grep temp
   ```
5. **Save checkpoints frequently** (already configured in script)
6. **Test with short texts first** before generating long audio

---

## 🎤 After Training

Once training completes successfully:

1. **Test the model** with various Hindi sentences
2. **Fine-tune** if quality is not satisfactory (adjust epochs, learning rate)
3. **Export the model** for production use
4. **Share results** with the team!

---

## ❓ Questions?

If you encounter any issues:
1. Check the error message carefully
2. Read TRAINING_GUIDE.md for detailed explanations
3. Check GitHub issues: https://github.com/paarth-error/hindi_tts/issues
4. Verify all steps were completed in order

---

**Good luck with training! 🚀🎯**

---

## 📝 Notes for Kiro

- This is a **complete, self-contained project**
- All preprocessing scripts are ready to run
- The main task is to **run Steps 2-7**, then **train with GPT-SoVITS**
- **Estimated total time:** 4-6 hours (including training)
- **Priority:** Ensure GPU is detected and used properly
- **Fallback:** If GPU issues, can train on CPU (will be slower)

Please proceed step-by-step, verifying each step completes successfully before moving to the next.
