# 🎤 Hindi TTS Training Guide for Mac M1

## Overview
Tumhare paas Apple M1 hai, toh MPS (Metal Performance Shaders) GPU acceleration use kar sakte ho. Yahaan 3 options hain with pros/cons.

---

## ✅ Option 1: GPT-SoVITS (Recommended)

### Why GPT-SoVITS?
- ✅ Best quality for Hindi
- ✅ Fast training (2-3 hours on M1)
- ✅ MPS support built-in
- ✅ Web UI included (easy to use)
- ✅ Few-shot learning (can clone voice with just 5-10 seconds)

### Installation
```bash
cd /Users/paarthchhikara/Downloads/hindi_tts
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
pip install -r requirements.txt
```

### Prepare Dataset
```bash
cd /Users/paarthchhikara/Downloads/hindi_tts/hindi_tts_dataset
python3 scripts/09_train_gpt_sovits_mac.py
```

### Start Training
```bash
cd ../GPT-SoVITS
python3 webui.py
```

Then open browser: `http://localhost:9874`

### Training Steps in Web UI:
1. **Upload dataset** → Select `dataset/hindi_tts/audio/`
2. **ASR** → Transcribe audio (uses Whisper)
3. **Train SoVITS** → Start training (~2 hours)
4. **Train GPT** → Start GPT training (~1 hour)
5. **Inference** → Test your model!

### Memory Requirements
- **Minimum**: 8GB RAM (M1 base model)
- **Recommended**: 16GB RAM (better batch size)

---

## ✅ Option 2: Coqui TTS XTTS-v2 (Open Source)

### Why XTTS?
- ✅ Fully open source
- ✅ Multi-speaker support
- ✅ Voice cloning capability
- ✅ Active community
- ❌ Training slower than GPT-SoVITS

### Installation
```bash
pip install TTS
```

### Prepare Dataset (Already Compatible!)
Our manifest.json format works directly with XTTS.

### Start Training
```bash
cd /Users/paarthchhikara/Downloads/hindi_tts/hindi_tts_dataset

# Convert manifest to XTTS format
python3 scripts/08_format_sovits.py --format xtts

# Train
tts-train \
  --config_path data/07_final/xtts_config.json \
  --model_name xtts \
  --device mps \
  --batch_size 4
```

### Training Time
- ~4-6 hours on M1
- Checkpoint every 1000 steps

---

## ✅ Option 3: Piper TTS (Fastest, Lightweight)

### Why Piper?
- ✅ Extremely fast inference
- ✅ Small model size (~10MB)
- ✅ Low resource usage
- ❌ Quality slightly lower
- ❌ Training setup more complex

### Installation
```bash
pip install piper-tts
```

### Training
Piper uses VITS architecture. Training requires:
1. Phonemized text
2. Specific audio format
3. Custom training script

Main recommend **GPT-SoVITS** for best results.

---

## 🎯 Recommended Workflow

### For Best Quality: GPT-SoVITS
```bash
# 1. Install GPT-SoVITS
cd /Users/paarthchhikara/Downloads/hindi_tts
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
pip install -r requirements.txt

# 2. Prepare dataset
cd ../hindi_tts_dataset
python3 scripts/09_train_gpt_sovits_mac.py

# 3. Start Web UI
cd ../GPT-SoVITS
python3 webui.py

# 4. Open browser and follow UI steps
```

### For Open Source: XTTS
```bash
# 1. Install
pip install TTS

# 2. Train
cd /Users/paarthchhikara/Downloads/hindi_tts/hindi_tts_dataset
python3 scripts/08_format_sovits.py --format xtts
tts-train --config_path data/07_final/xtts_config.json
```

---

## 📊 Training Tips for Mac M1

### Before Training:
1. ✅ Plug in your MacBook
2. ✅ Close unnecessary apps
3. ✅ Enable "Prevent sleeping" in caffeinate:
   ```bash
   caffeinate -disu &
   ```

### During Training:
- Monitor temperature:
  ```bash
  sudo powermetrics --samplers smc | grep -i temp
  ```
- Watch GPU usage:
  ```bash
  sudo powermetrics --samplers gpu_power | grep -i gpu
  ```

### If Out of Memory:
1. Reduce `batch_size` in config
2. Close Chrome/heavy apps
3. Restart Mac to clear memory

---

## 🔍 Dataset Quality Check

Before training, check your dataset:
```bash
cd /Users/paarthchhikara/Downloads/hindi_tts/hindi_tts_dataset
python3 scripts/06_export_manifest.py --stats
```

**Good Dataset Checklist:**
- ✅ 500+ samples (more = better)
- ✅ 2-15 seconds per clip
- ✅ Clear speech, no background noise
- ✅ Consistent speaker
- ✅ Proper transcriptions

---

## 🚀 After Training

### Test Your Model
```python
from TTS.api import TTS

# Load your trained model
tts = TTS(model_path="path/to/your/model")

# Generate speech
tts.tts_to_file(
    text="नमस्ते, यह एक टेस्ट है।",
    file_path="output.wav"
)
```

### Inference Speed on M1:
- **GPT-SoVITS**: ~1-2 seconds for 5-second audio
- **XTTS**: ~2-3 seconds
- **Piper**: ~0.1 seconds (fastest!)

---

## ❓ Troubleshooting

### "MPS not available"
```bash
python3 -c "import torch; print(torch.backends.mps.is_available())"
```
Should return `True` on M1 Mac.

### "Out of Memory"
Reduce batch_size in training config:
```json
{
  "train": {
    "batch_size": 4  // Try 4, 2, or even 1
  }
}
```

### "Training too slow"
1. Check if MPS is enabled: `device: mps`
2. Close background apps
3. Use smaller model size

---

## 📧 Need Help?

Issues? Check logs:
```bash
# GPT-SoVITS logs
cat GPT-SoVITS/logs/latest.log

# System logs
log show --predicate 'process == "Python"' --last 1h
```

---

**Recommendation: Start with GPT-SoVITS Web UI** — sabse easy aur best quality! 🎯
