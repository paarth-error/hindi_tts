# 🎤 CORRECTED Hindi TTS Training Prompt for Kiro

⚠️ **IMPORTANT: The previous training was incomplete. This is the CORRECT process.**

---

## 🚨 What Went Wrong Last Time

The previous run skipped critical steps:
- ❌ Only used 26 files (should be 500-2000 samples)
- ❌ Skipped vocal separation (Demucs)
- ❌ Skipped speaker diarization (Pyannote)
- ❌ Skipped transcription (Whisper)
- ❌ Trained on CPU instead of GPU
- ❌ Trained only 5 epochs instead of 100
- ❌ Fake loss of 0.000000 (model didn't actually train)

**Result:** The 4MB checkpoint is unusable for real TTS.

---

## ✅ CORRECT Process - Step by Step

### Prerequisites Check

**STOP and verify these before proceeding:**

1. **Check GPU availability:**
   ```bash
   # For NVIDIA GPU:
   nvidia-smi
   
   # For Mac:
   system_profiler SPHardwareDataType | grep Chip
   ```
   
   **REQUIREMENT:** Must have GPU (NVIDIA or Apple Silicon). CPU training = bad quality.

2. **Check disk space:**
   ```bash
   df -h
   ```
   
   **REQUIREMENT:** At least 25GB free space.

3. **Check Python version:**
   ```bash
   python3 --version
   ```
   
   **REQUIREMENT:** Python 3.10 or higher.

4. **Check if FFmpeg is installed:**
   ```bash
   ffmpeg -version
   ```
   
   **REQUIREMENT:** FFmpeg must be installed.
   - Windows: Download from https://ffmpeg.org/download.html
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

**⚠️ DO NOT PROCEED if any of the above fail.**

---

## 📥 Step 1: Clone Repository

```bash
# Clone the repo
git clone https://github.com/paarth-error/hindi_tts.git
cd hindi_tts/hindi_tts_dataset

# Verify you're in the right place
ls -la
# Should see: data/, scripts/, requirements.txt, README.md
```

---

## 🔧 Step 2: Setup Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(torch|demucs|pyannote|whisper)"
```

**Expected output:** Should show torch, demucs, pyannote.audio, openai-whisper installed.

---

## 🔑 Step 3: Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
# Add your actual tokens:
```

**Edit `.env` file with these values:**
```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxx
```

**How to get tokens:**
1. **HuggingFace Token:**
   - Go to: https://huggingface.co/settings/tokens
   - Create new token (Read access)
   - Accept Pyannote terms: https://huggingface.co/pyannote/speaker-diarization-3.1

2. **Groq API Key (optional):**
   - Go to: https://console.groq.com/keys
   - Create new key

**⚠️ Verify `.env` file has real tokens, not placeholders!**

```bash
# Check .env file
cat .env
# Should show actual tokens, not "your_token_here"
```

---

## 📊 Step 4: Verify Raw Audio Files

```bash
# Check if audio files exist
ls -lh data/01_raw_audio/

# Count files
ls data/01_raw_audio/*.wav | wc -l
# Should show 16 files
```

**Expected:** 16 WAV files from YouTube downloads.

**If files are missing:**
```bash
# Run YouTube scraper again
python3 scripts/01_scrape_youtube.py
```

---

## 🎵 Step 5: Vocal Separation (Demucs)

**THIS STEP IS CRITICAL - DO NOT SKIP!**

```bash
# Run Demucs to separate vocals from background music
python3 scripts/02_separate_audio.py

# This will take 30-60 minutes
# Wait for "✓ Vocal separation complete" message
```

**What happens:**
- Removes background music
- Extracts clean vocal tracks
- Output: `data/02_isolated_vocals/`

**Verify output:**
```bash
# Check separated vocals
ls -lh data/02_isolated_vocals/

# Count files
ls data/02_isolated_vocals/*.wav | wc -l
# Should show 16 files (same as input)
```

**⚠️ DO NOT PROCEED until you see 16 vocal files!**

---

## 🗣️ Step 6: Speaker Diarization (Pyannote)

**THIS STEP IS CRITICAL - DO NOT SKIP!**

```bash
# Run Pyannote to separate different speakers
python3 scripts/03_diarize_pyannote.py

# This will take 1-2 hours
# Uses GPU (check nvidia-smi or Activity Monitor for GPU usage)
# Wait for "✓ Diarization complete" message
```

**What happens:**
- Identifies different speakers in audio
- Splits audio into per-speaker segments
- Creates 500-2000 individual clips
- Output: `data/03_diarized_segments/SPEAKER_XX/`

**Verify output:**
```bash
# Check diarized segments
ls -lh data/03_diarized_segments/

# Count total clips
find data/03_diarized_segments/ -name "*.wav" | wc -l
# Should show 500-2000 files (NOT 26!)
```

**⚠️ CRITICAL CHECK:**
- If you see only 20-30 files → SOMETHING WENT WRONG
- You MUST have 500+ files for good TTS quality
- If count is low, check logs for errors

---

## 📝 Step 7: Transcription (Whisper)

**THIS STEP IS CRITICAL - DO NOT SKIP!**

```bash
# Run Whisper to transcribe audio to Hindi text
python3 scripts/04_transcribe_whisper.py

# This will take 1-2 hours
# Uses GPU
# Wait for "✓ Transcription complete" message
```

**What happens:**
- Converts speech to Devanagari text
- Creates text transcripts for each audio clip
- Output: `data/04_transcribed/`

**Verify output:**
```bash
# Check transcriptions
ls -lh data/04_transcribed/

# Check a sample transcript
cat data/04_transcribed/SPEAKER_00_00001.txt
# Should show Hindi Devanagari text
```

**⚠️ Verify transcripts contain actual Hindi text, not empty files!**

---

## 🤖 Step 8: LLM Tagging (Optional)

```bash
# Add metadata tags using Groq API
python3 scripts/05_llm_tag_groq.py

# This is OPTIONAL - can skip if slow or rate-limited
```

**Note:** This step adds quality/emotion tags. Not critical for basic TTS.

---

## 📦 Step 9: Create Training Manifest

```bash
# Export final manifest
python3 scripts/06_export_manifest.py

# Check output
cat data/07_final/manifest.json | head -20
```

**Verify manifest:**
```bash
# Count samples in manifest
cat data/07_final/manifest.json | grep -o '"audio_path"' | wc -l
# Should show 500+ entries
```

**⚠️ If manifest has < 500 samples, go back and check Step 6 (diarization)!**

---

## 📈 Step 10: Check Dataset Statistics

```bash
# View detailed statistics
python3 scripts/08_format_sovits.py --stats
```

**Expected output:**
```
📊 Dataset Statistics
══════════════════════════════════════════
Total samples: 500-2000
Total duration: 1-3 hours
Average duration: 3-8 seconds
Speakers: 2-3
══════════════════════════════════════════
```

**⚠️ STOP HERE if statistics look wrong:**
- Total samples < 500? → Go back to Step 6
- Average duration > 15 seconds? → Check chunking
- Speakers = 0? → Go back to Step 6

---

## 🏋️ Step 11: Install GPT-SoVITS

```bash
# Go to parent directory
cd ..

# Clone GPT-SoVITS
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())"
# Should print "CUDA available: True" (or check MPS for Mac)
```

---

## 🎯 Step 12: Prepare Dataset for Training

```bash
# Go back to project directory
cd ../hindi_tts_dataset

# Run dataset preparation
python3 scripts/09_train_gpt_sovits_mac.py

# This converts audio and creates training list
```

**Verify output:**
```bash
# Check converted audio files
ls -lh ../GPT-SoVITS/dataset/hindi_tts/audio/
# Should show 500+ WAV files at 32kHz

# Check training list
wc -l ../GPT-SoVITS/dataset/hindi_tts/train.list
# Should show 500+ lines
```

---

## 🚀 Step 13: Start ACTUAL Training

**CRITICAL: Use GPU, not CPU!**

```bash
cd ../GPT-SoVITS

# Check GPU is available
python3 -c "import torch; print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'MPS' if torch.backends.mps.is_available() else 'CPU')"
# Should NOT print "CPU"

# Start training with GPU
python3 GPT_SoVITS/s1_train.py \
  --config_path ../hindi_tts_dataset/data/07_final/config.json \
  --model_name hindi_tts \
  --device cuda  # Use 'cuda' for NVIDIA, 'mps' for Mac M1/M2/M3
  --epochs 100 \
  --batch_size 8
```

**OR use Web UI (easier):**
```bash
python3 webui.py
# Open browser: http://localhost:9874
# Select dataset and click "Start Training"
```

---

## ✅ Verify Real Training is Happening

**Watch for these signs:**

1. **GPU Usage:**
   ```bash
   # NVIDIA:
   watch -n 1 nvidia-smi
   # Should show GPU memory usage increasing
   
   # Mac:
   sudo powermetrics --samplers gpu_power
   # Should show GPU active
   ```

2. **Training Output:**
   ```
   Epoch 1/100: Loss=15.234
   Epoch 2/100: Loss=12.456
   Epoch 3/100: Loss=10.123
   ...
   ```

3. **Time Check:**
   - Epoch 1 should take 5-15 minutes
   - Total training: 2-6 hours
   - **If it finishes in < 1 hour → NOT REAL TRAINING!**

4. **Loss Values:**
   - Start: 10-20
   - Epoch 50: 2-5
   - Epoch 100: 0.5-1.5
   - **If loss = 0.000000 → FAKE TRAINING!**

5. **Model Size:**
   - Real model: 200-500 MB
   - **If < 10 MB → FAKE MODEL!**

---

## 📊 Monitor Training Progress

```bash
# Watch log file
tail -f logs/hindi_tts/train.log

# Check checkpoints
ls -lh logs/hindi_tts/checkpoints/
# Should see checkpoint_epoch_10.pth, checkpoint_epoch_20.pth, etc.
# Each should be 200-500 MB
```

---

## 🎤 Step 14: Test the Trained Model

**After training completes (2-6 hours):**

```bash
# Test inference
python3 inference.py \
  --checkpoint logs/hindi_tts/best_checkpoint.pth \
  --text "नमस्ते, यह एक टेस्ट है।" \
  --output test_output.wav

# Play the output
# Should sound like natural Hindi speech
```

---

## 🚨 RED FLAGS - Stop and Fix

**If you see any of these, STOP and investigate:**

1. ❌ Training finishes in < 1 hour
2. ❌ Model size < 50 MB
3. ❌ Loss = 0.000000
4. ❌ Only 26-30 audio samples in dataset
5. ❌ GPU not being used (check with nvidia-smi or Activity Monitor)
6. ❌ No vocal separation files in `data/02_isolated_vocals/`
7. ❌ No diarized segments in `data/03_diarized_segments/`
8. ❌ No transcriptions in `data/04_transcribed/`

**These indicate the process was skipped or faked!**

---

## ✅ SUCCESS CRITERIA

**Training is successful when:**

1. ✅ 500+ audio samples in dataset
2. ✅ Training took 2-6 hours
3. ✅ GPU was actively used (nvidia-smi showed usage)
4. ✅ Loss decreased from ~15 to ~1 over 100 epochs
5. ✅ Model checkpoint is 200-500 MB
6. ✅ Test audio sounds natural and clear
7. ✅ All intermediate steps (02-06) completed

---

## 💡 Hardware-Specific Settings

### For RTX 3060 (12GB):
```bash
--device cuda --batch_size 16 --fp16_run True
```

### For RTX 4090 (24GB):
```bash
--device cuda --batch_size 32 --fp16_run True
```

### For Mac M1 (8GB):
```bash
--device mps --batch_size 4 --fp16_run False
```

### For Mac M1 (16GB):
```bash
--device mps --batch_size 8 --fp16_run False
```

---

## 📝 Expected Timeline

```
Step 1-4: Setup                      → 30 minutes
Step 5: Vocal Separation (Demucs)    → 30-60 minutes
Step 6: Diarization (Pyannote)       → 1-2 hours
Step 7: Transcription (Whisper)      → 1-2 hours
Step 8: LLM Tagging (optional)       → 30 minutes
Step 9-12: Setup Training            → 30 minutes
Step 13: ACTUAL Training             → 2-6 hours
────────────────────────────────────────────────
TOTAL: 6-12 hours
```

**⚠️ If total time < 4 hours → Something was skipped!**

---

## 🆘 Troubleshooting

### "Out of Memory" during Demucs
```bash
# Edit scripts/02_separate_audio.py
# Change device="cuda" to device="cpu" in Demucs call
```

### "Pyannote 403 Error"
```bash
# 1. Go to https://huggingface.co/pyannote/speaker-diarization-3.1
# 2. Click "Agree and access repository"
# 3. Verify HF_TOKEN in .env is correct
```

### "CUDA out of memory" during training
```bash
# Reduce batch_size
--batch_size 4  # or even 2
```

### "Training too slow on CPU"
**YOU MUST USE GPU!** CPU training will take days and produce bad quality.
- Get access to GPU laptop
- Use cloud GPU (Kaggle, Colab, RunPod)
- Or buy cloud GPU time

---

## 📞 How to Verify Each Step Completed

After EACH step, run these verification commands:

**After Step 5 (Demucs):**
```bash
ls data/02_isolated_vocals/*.wav | wc -l
# MUST show 16 files
```

**After Step 6 (Pyannote):**
```bash
find data/03_diarized_segments/ -name "*.wav" | wc -l
# MUST show 500+ files
```

**After Step 7 (Whisper):**
```bash
ls data/04_transcribed/*.txt | wc -l
# MUST show 500+ files
```

**After Step 9 (Manifest):**
```bash
cat data/07_final/manifest.json | grep -o '"audio_path"' | wc -l
# MUST show 500+ entries
```

**After Step 13 (Training):**
```bash
ls -lh logs/hindi_tts/checkpoints/best_checkpoint.pth
# MUST be 200-500 MB, NOT 4 MB!
```

---

## ✅ Final Checklist

Before considering training "complete":

- [ ] Demucs ran successfully (16 vocal files created)
- [ ] Pyannote ran successfully (500+ segments created)
- [ ] Whisper ran successfully (500+ transcriptions created)
- [ ] Manifest has 500+ samples
- [ ] Training used GPU (verified with nvidia-smi/Activity Monitor)
- [ ] Training took 2+ hours
- [ ] Loss decreased from ~15 to ~1
- [ ] Final model is 200+ MB
- [ ] Test audio sounds natural

**ALL boxes must be checked!**

---

**Good luck! This time do it properly. No shortcuts!** 🚀
