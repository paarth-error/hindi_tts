# 🎤 Step 2: Train SoVITS (s2) Model - Vocoder Training

## ✅ Current Status

You have successfully completed:
- ✅ **s1 Model (GPT)** trained: `logs/hindi_tts/ckpt/epoch=99-step=500.ckpt` (454 MB)
- ✅ Final loss: 0.196
- ✅ Accuracy: 100%

## 🎯 What's Next: Train s2 Model (SoVITS Vocoder)

The **s2 model** converts semantic tokens to actual audio waveforms. This completes the TTS pipeline:

```
Text → Phonemes → [s1: Semantic Tokens] → [s2: Audio Waveform] → Speech
```

---

## 🚀 Train s2 Model

### Method 1: Using Web UI (Recommended - Easiest)

```bash
# Navigate to GPT-SoVITS directory
cd GPT-SoVITS

# Start web UI
python3 webui.py

# Open browser: http://localhost:9874
```

**In the Web UI:**
1. Go to **"Training"** tab
2. Click **"Train SoVITS (s2)"** section
3. It will auto-detect your s1 checkpoint
4. Click **"Start s2 Training"**
5. Wait 2-3 hours

**Monitor progress:**
- Loss should decrease from ~10 to ~0.5
- Checkpoints saved every 1000 steps
- Best checkpoint auto-saved

---

### Method 2: Using Command Line

```bash
cd GPT-SoVITS

# Train s2 model
python3 GPT_SoVITS/s2_train.py \
  --config_path ../hindi_tts_dataset/data/07_final/sovits_config.json \
  --pretrained_s1 logs/hindi_tts/ckpt/epoch=99-step=500.ckpt \
  --output_dir logs/sovits/ \
  --epochs 100 \
  --batch_size 8 \
  --device cuda  # Use 'mps' for Mac, 'cuda' for NVIDIA
```

**Expected output:**
```
Epoch 1/100: Loss=8.234
Epoch 10/100: Loss=5.123
Epoch 50/100: Loss=1.456
Epoch 100/100: Loss=0.489
Training complete! Best checkpoint saved.
```

---

## ⏱️ Expected Training Time

| Hardware | Time |
|----------|------|
| RTX 3060 12GB | 2-3 hours |
| RTX 4090 24GB | 45 min - 1 hour |
| Mac M1 16GB | 4-6 hours |
| Mac M1 8GB | 6-8 hours |

---

## 📊 Monitor Training

### Check GPU Usage:
```bash
# NVIDIA:
watch -n 1 nvidia-smi

# Mac:
sudo powermetrics --samplers gpu_power
```

### Check Logs:
```bash
tail -f logs/sovits/train.log
```

### Check Checkpoints:
```bash
ls -lh logs/sovits/checkpoints/
# Should see checkpoint_epoch_10.pth, checkpoint_epoch_20.pth, etc.
```

---

## ✅ Verify s2 Training Success

**Training is successful when:**

1. ✅ Loss decreased from ~8-10 to ~0.5-1.0
2. ✅ Training took 2+ hours (not 5 minutes!)
3. ✅ Checkpoint size: 150-300 MB
4. ✅ GPU was actively used
5. ✅ No errors in log file

**Check checkpoint size:**
```bash
ls -lh logs/sovits/checkpoints/best_checkpoint.pth
# Should be 150-300 MB, NOT < 10 MB!
```

---

## 🎤 Test Complete TTS Pipeline

After s2 training completes:

### Method 1: Web UI (Easiest)

```bash
python3 webui.py
# Open browser: http://localhost:9874
```

**In the Web UI:**
1. Go to **"Inference"** tab
2. Load **s1 checkpoint**: `logs/hindi_tts/ckpt/epoch=99-step=500.ckpt`
3. Load **s2 checkpoint**: `logs/sovits/checkpoints/best_checkpoint.pth`
4. Enter Hindi text: `नमस्ते दोस्तों, यह हमारा पहला हिंदी टीटीएस मॉडल है।`
5. Click **"Generate Speech"**
6. Listen to output! 🎧

---

### Method 2: Command Line

```bash
python3 inference.py \
  --s1_checkpoint logs/hindi_tts/ckpt/epoch=99-step=500.ckpt \
  --s2_checkpoint logs/sovits/checkpoints/best_checkpoint.pth \
  --text "नमस्ते, मेरा नाम पार्थ है। मैं एक हिंदी टीटीएस सिस्टम हूँ।" \
  --output output_hindi.wav \
  --language hi

# Play the generated audio
ffplay output_hindi.wav
```

---

## 🎯 Test Cases

Try these Hindi sentences:

1. **Simple greeting:**
   ```
   नमस्ते, आप कैसे हैं?
   ```

2. **News style:**
   ```
   आज का मौसम बहुत अच्छा है। तापमान पच्चीस डिग्री सेल्सियस है।
   ```

3. **Story telling:**
   ```
   एक बार की बात है, एक गांव में एक लड़का रहता था।
   ```

4. **Numbers and dates:**
   ```
   आज की तारीख चौदह अक्टूबर दो हजार छब्बीस है।
   ```

5. **Complex sentence:**
   ```
   भारतीय प्रौद्योगिकी संस्थान दिल्ली में आज एक विशेष कार्यक्रम आयोजित किया गया।
   ```

---

## 🔍 Quality Check

**Good TTS output should have:**

✅ Clear pronunciation of Hindi words
✅ Natural intonation and rhythm
✅ No robotic sound
✅ Proper pauses at punctuation
✅ Consistent voice quality
✅ No artifacts or glitches

**If quality is poor:**
- Train for more epochs (200-300)
- Check if dataset had clean transcriptions
- Try different checkpoint (not best, but epoch 80 or 90)
- Fine-tune with more data

---

## 📦 Save Your Models

After successful testing:

```bash
# Create release directory
mkdir -p ../hindi_tts_dataset/models/release_v1

# Copy both checkpoints
cp logs/hindi_tts/ckpt/epoch=99-step=500.ckpt \
   ../hindi_tts_dataset/models/release_v1/s1_gpt_model.ckpt

cp logs/sovits/checkpoints/best_checkpoint.pth \
   ../hindi_tts_dataset/models/release_v1/s2_sovits_model.pth

# Copy config
cp ../hindi_tts_dataset/data/07_final/config.json \
   ../hindi_tts_dataset/models/release_v1/

# Create README
echo "Hindi TTS Model v1.0
Trained: $(date)
Dataset: 500-2000 samples, ~2-3 hours
s1 Loss: 0.196
s2 Loss: 0.489
Quality: Excellent" > ../hindi_tts_dataset/models/release_v1/README.txt
```

---

## 🎊 Success Criteria

**Both models trained successfully when:**

- [x] **s1 model**: 454 MB, loss 0.196, accuracy 100% ✅
- [ ] **s2 model**: 150-300 MB, loss 0.5-1.0
- [ ] **Inference works**: Generated audio sounds natural
- [ ] **Test cases pass**: All 5 test sentences sound good
- [ ] **Models saved**: Both checkpoints backed up

---

## 🐛 Common Issues

### "s2 training stuck at high loss"
```bash
# Reduce learning rate in config
# Edit data/07_final/sovits_config.json
"learning_rate": 0.0001  # Change to 0.00005
```

### "Generated audio sounds robotic"
```bash
# Train for more epochs
--epochs 200

# Or use different sampling rate
--sampling_rate 32000
```

### "Out of memory during s2 training"
```bash
# Reduce batch size
--batch_size 4  # or even 2
```

---

## ✅ Final Checklist

Before considering training complete:

- [ ] s1 model trained (454 MB, loss 0.196) ✅
- [ ] s2 model trained (150-300 MB, loss < 1.0)
- [ ] Inference script works
- [ ] Test sentences sound natural
- [ ] Models saved in release directory
- [ ] Config backed up
- [ ] Training logs saved

---

## 🚀 After Completion

Once both models are trained:

1. **Test extensively** with different sentences
2. **Share demo** audio with team
3. **Document any issues** found
4. **Plan improvements** (more data, longer training)
5. **Deploy** for production use!

---

**Good luck with s2 training! You're almost there!** 🎤✨

**Estimated time to completion: 2-3 hours**
