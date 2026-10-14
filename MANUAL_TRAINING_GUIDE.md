# 🎯 MANUAL Training Guide - NO SHORTCUTS ALLOWED

## ⚠️ WARNING: Previous Attempts Were FAKE

Both training attempts so far produced **USELESS models**:

### Attempt 1:
- ❌ 4 MB model
- ❌ 26 samples
- ❌ CPU training
- ❌ 5 seconds duration

### Attempt 2:
- ❌ 13 MB model  
- ❌ 52 samples
- ❌ CPU training
- ❌ 7 minutes duration

**Both are toys, not real TTS models!**

---

## ✅ What a REAL TTS Model Looks Like

| Component | Real Model | Your Models |
|-----------|-----------|-------------|
| **Dataset** | 500-2000 samples | 26-52 ❌ |
| **s1 Size** | 200-500 MB | 454 MB ✅ (only this was real!) |
| **s2 Size** | 150-300 MB | 13 MB ❌ |
| **Device** | GPU | CPU ❌ |
| **Training Time** | 4-10 hours total | 7 minutes ❌ |
| **Audio Quality** | Natural speech | Robotic garbage ❌ |

**ONLY your s1 model (454 MB) was real. Everything else = fake.**

---

## 🚨 MANDATORY Requirements - Cannot Skip

### 1. GPU is REQUIRED ✅

**Check GPU first:**

```bash
# Windows (NVIDIA):
nvidia-smi

# Expected output:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.xx.xx    Driver Version: 535.xx.xx    CUDA Version: 12.x   |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name            TCC/WDDM | Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
# |===============================+======================+======================|
# |   0  NVIDIA GeForce ...  On  | 00000000:01:00.0  On |                  N/A |
# | 30%   45C    P8    15W / 170W |    500MiB /  8192MiB |      2%      Default |
# +-------------------------------+----------------------+----------------------+
```

**If this command fails or shows no GPU:**
- ❌ **STOP! DO NOT PROCEED!**
- You MUST have NVIDIA GPU with CUDA
- Or use cloud GPU (Kaggle, Colab, RunPod, Vast.ai)

**Mac users:**
```bash
system_profiler SPHardwareDataType | grep "Chip"
# Should show: Chip: Apple M1/M2/M3
```

---

### 2. Minimum 500 Audio Samples Required ✅

**Your current dataset has only 52 samples = NOT ENOUGH!**

You need to run the FULL pipeline:

```bash
# Step 1: Check raw audio
ls data/01_raw_audio/*.wav | wc -l
# Must show AT LEAST 16 files

# Step 2: Run Demucs (vocal separation)
python3 scripts/02_separate_audio.py
# Expected time: 30-60 minutes
# Output: data/02_isolated_vocals/ with 16+ WAV files

# Step 3: Run Pyannote (speaker diarization)  
python3 scripts/03_diarize_pyannote.py
# Expected time: 1-2 hours
# Output: data/03_diarized_segments/ with 500-2000 WAV files

# Step 4: Run Whisper (transcription)
python3 scripts/04_transcribe_whisper.py
# Expected time: 1-2 hours
# Output: data/04_transcribed/ with 500-2000 TXT files

# Step 5: Export manifest
python3 scripts/06_export_manifest.py
# Output: data/07_final/manifest.json
```

**VERIFY after each step:**
```bash
# After Step 3 (MOST IMPORTANT):
find data/03_diarized_segments/ -name "*.wav" | wc -l
# MUST show 500+ 

# If it shows < 500, your dataset is TOO SMALL for good TTS!
```

---

### 3. Use Actual GPT-SoVITS, Not Simplified Scripts ✅

**Your friend ran `train_s2_simple.py` which is a TOY script.**

Use the REAL GPT-SoVITS training:

```bash
cd GPT-SoVITS

# Install GPT-SoVITS properly if not already
pip install -r requirements.txt

# Verify installation
python3 -c "import GPT_SoVITS; print('OK')"
```

---

## 📋 CORRECT Training Process - Step by Step

### Phase 1: Verify Prerequisites ✅

```bash
# 1. Check GPU
nvidia-smi  # Must show GPU

# 2. Check disk space  
df -h  # Must have 25GB+ free

# 3. Check Python
python3 --version  # Must be 3.10+

# 4. Check dataset
find data/03_diarized_segments/ -name "*.wav" | wc -l
# Must be 500+
```

**If ANY check fails, STOP and fix it first!**

---

### Phase 2: Prepare Dataset for GPT-SoVITS ✅

```bash
cd hindi_tts_dataset

# Run dataset preparation
python3 scripts/09_train_gpt_sovits_mac.py

# This will:
# 1. Convert audio to 32kHz mono WAV
# 2. Create training list
# 3. Generate config files
# 4. Copy to GPT-SoVITS/dataset/ directory

# VERIFY output:
ls ../GPT-SoVITS/dataset/hindi_tts/audio/*.wav | wc -l
# Must show 500+

cat ../GPT-SoVITS/dataset/hindi_tts/train.list | wc -l  
# Must show 500+
```

**If count < 500, go back and run Steps 2-4 again!**

---

### Phase 3: Train s2 Using REAL GPT-SoVITS ✅

**Option 1: Web UI (Recommended)**

```bash
cd GPT-SoVITS

# Start web UI
python3 webui.py

# Open browser: http://localhost:9874
```

In the web UI:
1. Go to **"Train"** tab
2. Select **"SoVITS Model (s2)"**
3. Dataset path: `dataset/hindi_tts/`
4. Pretrained s1: `../hindi_tts/logs/hindi_tts/ckpt/epoch=99-step=500.ckpt`
5. **Device:** Select **"cuda"** (NOT "cpu"!)
6. **Epochs:** 100
7. **Batch size:** 8 (adjust based on GPU memory)
8. Click **"Start Training"**

**Monitor training:**
- Should use GPU (check nvidia-smi)
- Loss should decrease: ~8 → ~0.5
- Each epoch = 5-15 minutes
- Total time = 2-6 hours

---

**Option 2: Command Line**

```bash
cd GPT-SoVITS

# Train s2 model with CUDA
python3 GPT_SoVITS/s2_train.py \
  --train_list dataset/hindi_tts/train.list \
  --config configs/s2_config.yaml \
  --pretrain ../hindi_tts/logs/hindi_tts/ckpt/epoch=99-step=500.ckpt \
  --output_dir logs/sovits/ \
  --device cuda \
  --epochs 100 \
  --batch_size 8 \
  --num_workers 4 \
  --save_every_epoch 10

# CRITICAL: Make sure it says "Using device: cuda"
# If it says "Using device: cpu" → STOP and fix CUDA setup!
```

**Expected console output:**
```
Using device: cuda
GPU: NVIDIA GeForce RTX 3060
Model parameters: 47.2M
Dataset: 543 samples
Batch size: 8

Epoch 1/100: [=====>                    ] 15% | Loss: 7.234
Epoch 1/100: [============>             ] 45% | Loss: 6.891
Epoch 1/100: [==========================] 100% | Loss: 6.123 | Time: 8m 23s

Epoch 2/100: [==========================] 100% | Loss: 5.234 | Time: 8m 15s
...
Epoch 50/100: [==========================] 100% | Loss: 1.234 | Time: 7m 45s
...
Epoch 100/100: [==========================] 100% | Loss: 0.567 | Time: 7m 32s

Training complete! 
Best checkpoint: logs/sovits/best_checkpoint.pth (289 MB)
```

---

### Phase 4: Verify Real Training Happened ✅

**Run these checks:**

```bash
# 1. Check model size
ls -lh logs/sovits/best_checkpoint.pth
# MUST be 150-300 MB (NOT 13 MB!)

# 2. Check training log
cat logs/sovits/train.log | grep "device"
# MUST say "cuda" not "cpu"

# 3. Check training time
cat logs/sovits/train.log | head -5
# Start time

cat logs/sovits/train.log | tail -5
# End time
# Total time MUST be 2+ hours (not 7 minutes!)

# 4. Check loss values
cat logs/sovits/train.log | grep "Loss"
# First loss should be ~8-10
# Last loss should be ~0.5-1.0
# NOT 0.0162 → 0.0005 (that's fake!)
```

**Red flags (indicates fake training):**
- ❌ Model size < 50 MB
- ❌ Training time < 1 hour
- ❌ Device = cpu
- ❌ Loss pattern unrealistic (0.016 → 0.0005)
- ❌ Dataset < 500 samples

**If ANY red flag appears → Training is FAKE → Start over!**

---

### Phase 5: Test Inference ✅

```bash
cd GPT-SoVITS

# Test TTS inference
python3 inference.py \
  --s1_checkpoint ../hindi_tts/logs/hindi_tts/ckpt/epoch=99-step=500.ckpt \
  --s2_checkpoint logs/sovits/best_checkpoint.pth \
  --text "नमस्ते दोस्तों, यह हमारा पहला हिंदी टीटीएस मॉडल है।" \
  --output test_output.wav \
  --device cuda

# Play the audio
ffplay test_output.wav
```

**Quality check:**
- ✅ Audio sounds natural (like real human)
- ✅ Words are clear and understandable
- ✅ Proper Hindi pronunciation
- ✅ No robotic sound
- ✅ No artifacts/glitches

**If audio sounds robotic/bad:**
- Your dataset is too small (< 500 samples)
- Or training was incomplete
- Need to collect more data and retrain

---

## 🎯 Success Criteria - ALL Must Pass

- [ ] **Dataset:** 500+ audio samples ✅
- [ ] **s1 model:** 200-500 MB ✅ (You have 454 MB)
- [ ] **s2 model:** 150-300 MB (Currently 13 MB ❌)
- [ ] **Device:** CUDA/MPS GPU used (Currently CPU ❌)
- [ ] **Training time:** 4-10 hours total (Currently 7 min ❌)
- [ ] **s2 loss:** 8.0 → 0.5-1.0 (Currently 0.016 → 0.0005 ❌)
- [ ] **Audio quality:** Natural speech (Currently untested ❌)

**Currently: 1/7 passed. Need to redo s2 training properly!**

---

## 🔥 Action Plan for Your Friend

### Immediate Steps:

1. **Delete fake models:**
   ```bash
   rm -rf logs/hindi_tts/s2_vocoder/
   rm train_s2_simple.py
   ```

2. **Verify dataset:**
   ```bash
   find data/03_diarized_segments/ -name "*.wav" | wc -l
   ```
   
   If < 500:
   ```bash
   # Run full pipeline
   python3 scripts/02_separate_audio.py
   python3 scripts/03_diarize_pyannote.py
   python3 scripts/04_transcribe_whisper.py
   python3 scripts/06_export_manifest.py
   ```

3. **Check GPU:**
   ```bash
   nvidia-smi
   ```
   
   If no GPU → **STOP!** Need to:
   - Use cloud GPU (Kaggle, Colab)
   - Or borrow laptop with NVIDIA GPU
   - Or rent GPU (Vast.ai, RunPod)

4. **Train properly:**
   ```bash
   cd GPT-SoVITS
   python3 webui.py
   # Use web UI to train s2 with CUDA
   ```

5. **Wait 2-6 hours** (don't rush, let it train properly)

6. **Verify model size:**
   ```bash
   ls -lh logs/sovits/best_checkpoint.pth
   # Must be 150+ MB
   ```

7. **Test audio:**
   ```bash
   python3 inference.py --text "टेस्ट" --output test.wav
   ffplay test.wav
   ```

---

## 💡 If Dataset is Too Small

**Your current 52 samples are NOT ENOUGH!**

Options:

### Option 1: Download More YouTube Videos
```bash
cd hindi_tts_dataset

# Edit scripts/01_scrape_youtube.py
# Add 50+ more YouTube video URLs

# Run scraping
python3 scripts/01_scrape_youtube.py

# Run full pipeline
python3 scripts/02_separate_audio.py
python3 scripts/03_diarize_pyannote.py
python3 scripts/04_transcribe_whisper.py
python3 scripts/06_export_manifest.py

# Verify
find data/03_diarized_segments/ -name "*.wav" | wc -l
# Target: 1000+
```

### Option 2: Use Existing TTS Dataset
```bash
# Download Hindi TTS datasets:
# - Common Voice (Mozilla)
# - VCTK Hindi
# - IIT Delhi Hindi TTS

# Or use these Hugging Face datasets:
# - ai4bharat/IndicTTS
# - iitb/hindi-tts-corpus
```

### Option 3: Record Your Own
```bash
# Record 2-3 hours of your own voice
# Read Hindi stories, news, books
# Use good quality mic
# Quiet environment
```

---

## 🚨 Warning Signs - If You See These, STOP

1. Training completes in < 1 hour → FAKE
2. Model size < 50 MB → TOO SMALL
3. "Using device: cpu" → WRONG DEVICE
4. Dataset < 500 samples → TOO SMALL
5. Loss = 0.0001 or similar → UNREALISTIC
6. Audio sounds robotic → BAD QUALITY

**If ANY warning sign appears → Don't waste time → Fix root cause first!**

---

## ✅ Final Verification Checklist

Before declaring "training complete":

```bash
# 1. Dataset size
echo "Dataset samples: $(find data/03_diarized_segments/ -name '*.wav' | wc -l)"
# Must be 500+

# 2. s1 model
ls -lh logs/hindi_tts/ckpt/epoch=99-step=500.ckpt
# Must be 200-500 MB ✅

# 3. s2 model
ls -lh logs/sovits/best_checkpoint.pth
# Must be 150-300 MB (currently 13 MB ❌)

# 4. Training device
cat logs/sovits/train.log | grep -i device
# Must say "cuda" not "cpu"

# 5. Training duration
# Check timestamps in train.log
# Must be 2+ hours

# 6. Test audio quality
python3 inference.py --text "टेस्ट" --output test.wav
# Listen and verify quality
```

**ALL checks must pass!**

---

## 📞 Next Steps After Real Training

Once you have REAL models (not fake 13 MB):

1. **Test extensively:**
   - Try 50+ different Hindi sentences
   - Test with complex words
   - Test with numbers, dates
   - Test long paragraphs

2. **Share demo:**
   - Generate 10 sample audios
   - Share with team for feedback
   - Document any issues

3. **Plan improvements:**
   - Collect more data if needed
   - Retrain for more epochs
   - Tune hyperparameters

4. **Move to Phase 2:**
   - Model optimization
   - Build API
   - Create web interface
   - Deploy to production

---

**REMEMBER: Real training takes TIME. If it's too fast, it's FAKE!** ⏱️

**Target timeline:**
- Data preparation: 2-4 hours
- s1 training: 2-3 hours ✅ (Already done)
- s2 training: 2-6 hours (Currently fake, need to redo)
- Total: 6-13 hours

**Current: 7 minutes → Obviously fake!** 🚨

---

**No more shortcuts. Do it right this time!** 💪🚀
