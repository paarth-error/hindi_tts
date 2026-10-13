# 🎯 Quick Setup Guide for Your Friend

Hey! This is a complete Hindi TTS training project. Everything is ready - just follow these steps.

---

## 📦 What You're Getting

A **complete pipeline** to train a Hindi Text-to-Speech model:
- ✅ 16 YouTube videos already downloaded & processed (2-3 hours of audio)
- ✅ All Python scripts ready to run
- ✅ Supports Mac M1/M2/M3 and NVIDIA GPUs
- ✅ Training guide with 3 different TTS frameworks
- ✅ Estimated training time: 2-6 hours (depending on hardware)

---

## 🚀 Two Options to Get Started

### Option 1: Using Kiro AI (Recommended - Easiest!)

If you have **Kiro IDE** installed:

1. **Open Kiro IDE**
2. **Clone this repo:**
   ```bash
   git clone https://github.com/paarth-error/hindi_tts.git
   cd hindi_tts/hindi_tts_dataset
   ```

3. **Open file:** `KIRO_PROMPT_FOR_TRAINING.md`

4. **Copy the entire content** of that file

5. **Paste it into Kiro chat** and press Enter

6. **Kiro will automatically:**
   - Check your system (GPU, disk space, Python version)
   - Install all dependencies
   - Run the data processing pipeline (Steps 2-7)
   - Install GPT-SoVITS
   - Prepare dataset for training
   - Start training with optimal settings
   - Monitor progress and save checkpoints

**Just sit back and watch! Kiro handles everything.** ☕

---

### Option 2: Manual Setup (If No Kiro)

If you **don't have Kiro IDE**, follow these steps manually:

#### Step 1: Check Your System

You need:
- [ ] Python 3.10 or higher
- [ ] GPU (NVIDIA or Apple Silicon M1/M2/M3)
- [ ] 20GB+ free disk space
- [ ] FFmpeg installed

Check:
```bash
python3 --version        # Should be 3.10+
nvidia-smi              # For NVIDIA GPU
# OR
system_profiler SPHardwareDataType | grep Chip  # For Mac
df -h                   # Check disk space
ffmpeg -version         # Should be installed
```

#### Step 2: Clone and Setup

```bash
# Clone repository
git clone https://github.com/paarth-error/hindi_tts.git
cd hindi_tts/hindi_tts_dataset

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Get API Keys

1. **HuggingFace Token:**
   - Go to: https://huggingface.co/settings/tokens
   - Create a new token
   - Accept Pyannote model terms: https://huggingface.co/pyannote/speaker-diarization-3.1

2. **Groq API Key:**
   - Go to: https://console.groq.com/keys
   - Create a new API key

3. **Add to .env file:**
   ```bash
   cp .env.example .env
   nano .env  # or use any text editor
   ```
   
   Add your keys:
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
   ```

#### Step 4: Run Data Processing Pipeline

```bash
# Step 2: Separate vocals (removes background music)
python3 scripts/02_separate_audio.py

# Step 3: Separate speakers (diarization)
python3 scripts/03_diarize_pyannote.py

# Step 4: Transcribe audio to Hindi text
python3 scripts/04_transcribe_whisper.py

# Step 5: Add LLM metadata (optional, can skip if slow)
python3 scripts/05_llm_tag_groq.py

# Step 6: Create training manifest
python3 scripts/06_export_manifest.py

# Step 7: Check dataset stats
python3 scripts/08_format_sovits.py --stats
```

**Expected time:** 2-4 hours total

#### Step 5: Install GPT-SoVITS

```bash
# Go to parent directory
cd ..

# Clone GPT-SoVITS
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS

# Install dependencies
pip install -r requirements.txt
```

#### Step 6: Prepare Dataset for Training

```bash
cd ../hindi_tts_dataset
python3 scripts/09_train_gpt_sovits_mac.py
```

#### Step 7: Start Training

**Option A: Web UI (Easiest)**
```bash
cd ../GPT-SoVITS
python3 webui.py
```
Then open browser: `http://localhost:9874`

**Option B: Command Line**
```bash
cd ../GPT-SoVITS
python3 GPT_SoVITS/s1_train.py \
  --config_path ../hindi_tts_dataset/data/07_final/config.json \
  --model_name hindi_tts \
  --device cuda  # Use 'mps' for Mac, 'cuda' for NVIDIA
```

---

## 📊 What to Expect

### Dataset Stats (After Processing)
- **Samples:** 500-2000 audio clips
- **Duration:** 1-3 hours total
- **Speakers:** 2-3 distinct voices
- **Quality:** Clean Hindi speech, no background music

### Training Progress
- **Epoch 1:** Loss ~15-20 (high, normal)
- **Epoch 50:** Loss ~2-5 (improving)
- **Epoch 100:** Loss ~0.5-1.5 (good quality)
- **Best checkpoint:** Usually around epoch 70-90

### Hardware Performance
| Your Hardware | Batch Size | Training Time |
|--------------|-----------|---------------|
| Mac M1 8GB | 4 | 4-6 hours |
| Mac M1 16GB | 8 | 2-3 hours |
| RTX 3060 12GB | 16 | 1-2 hours |
| RTX 4090 24GB | 32 | 30-45 min |

---

## 🐛 Common Issues & Fixes

### "Out of Memory"
```bash
# Edit config file and reduce batch_size
# Change from 8 to 4 or 2
```

### "Pyannote 403 Error"
- Make sure you accepted model terms: https://huggingface.co/pyannote/speaker-diarization-3.1
- Check your HF_TOKEN in .env file

### "Disk space full"
```bash
# Clear pip cache
pip cache purge

# Check large folders
du -sh * | sort -rh | head -10
```

### "CUDA not available"
- Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- Or use CPU (slower): `--device cpu`

---

## 📚 Detailed Documentation

All in the repo:
- **README.md** - Project overview
- **TRAINING_GUIDE.md** - Complete training guide (3 options: GPT-SoVITS, XTTS, Piper)
- **KIRO_PROMPT_FOR_TRAINING.md** - Full Kiro AI prompt

---

## 💡 Pro Tips

1. **Keep laptop plugged in** during training
2. **Close heavy apps** (Chrome, VS Code) to free RAM
3. **Monitor GPU temperature:**
   ```bash
   # NVIDIA: watch -n 1 nvidia-smi
   # Mac: sudo powermetrics --samplers smc | grep temp
   ```
4. **Training runs in background** - you can do other work
5. **Checkpoints auto-saved** - if it crashes, can resume

---

## 🎯 Quick Start Summary

**With Kiro (5 minutes setup):**
```bash
git clone https://github.com/paarth-error/hindi_tts.git
cd hindi_tts/hindi_tts_dataset
# Open KIRO_PROMPT_FOR_TRAINING.md
# Copy-paste into Kiro → Done! ✅
```

**Without Kiro (2-3 hours setup):**
```bash
git clone https://github.com/paarth-error/hindi_tts.git
cd hindi_tts/hindi_tts_dataset
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
# Run scripts 02-06 → Install GPT-SoVITS → Train
```

---

## 📞 Need Help?

- **GitHub Issues:** https://github.com/paarth-error/hindi_tts/issues
- **Documentation:** Read TRAINING_GUIDE.md
- **Logs:** Check terminal output for error messages

---

## ✅ Final Checklist Before Starting

- [ ] Python 3.10+ installed
- [ ] GPU available (NVIDIA or Apple Silicon)
- [ ] 20GB+ free disk space
- [ ] FFmpeg installed
- [ ] HuggingFace token obtained
- [ ] Groq API key obtained (optional for Step 5)
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured

**All set? Let's train! 🚀**

---

**Good luck! The model quality will be amazing.** 🎤✨

**Training time:** ~2-6 hours total  
**Expected quality:** Near-human for single speaker Hindi TTS

---

Made with ❤️ by Paarth
