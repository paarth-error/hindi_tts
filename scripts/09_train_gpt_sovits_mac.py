#!/usr/bin/env python3
"""
Step 9: Train GPT-SoVITS model on Mac with MPS acceleration
Converts our dataset to GPT-SoVITS format and trains
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
MANIFEST_FILE = BASE_DIR / "data" / "07_final" / "manifest.json"
SOVITS_DIR = BASE_DIR.parent / "GPT-SoVITS"
DATASET_DIR = SOVITS_DIR / "dataset" / "hindi_tts"

# ── Configuration ────────────────────────────────────────────────────────────
MIN_DURATION = 2.0  # seconds
MAX_DURATION = 15.0  # seconds
SAMPLE_RATE = 32000  # GPT-SoVITS uses 32kHz

def check_gpt_sovits_installed():
    """Check if GPT-SoVITS is installed"""
    if not SOVITS_DIR.exists():
        print("\n❌ GPT-SoVITS not found!")
        print("\n📥 Installing GPT-SoVITS...")
        print("\nRun these commands:")
        print("  cd", BASE_DIR.parent)
        print("  git clone https://github.com/RVC-Boss/GPT-SoVITS.git")
        print("  cd GPT-SoVITS")
        print("  pip install -r requirements.txt")
        return False
    return True

def convert_audio_format(input_path: Path, output_path: Path):
    """Convert audio to GPT-SoVITS format (32kHz, mono, WAV)"""
    cmd = [
        "ffmpeg", "-i", str(input_path),
        "-ar", str(SAMPLE_RATE),
        "-ac", "1",  # mono
        "-y",
        str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def prepare_dataset():
    """Convert our dataset to GPT-SoVITS format"""
    
    if not MANIFEST_FILE.exists():
        print(f"❌ Manifest file not found: {MANIFEST_FILE}")
        print("   Run scripts 01-06 first!")
        return False
    
    print("\n📂 Loading manifest...")
    with open(MANIFEST_FILE) as f:
        manifest = json.load(f)
    
    print(f"   Found {len(manifest['samples'])} samples")
    
    # Create dataset directories
    audio_dir = DATASET_DIR / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare training list
    train_list = []
    valid_samples = 0
    
    print("\n🔄 Converting audio files...")
    for i, sample in enumerate(manifest["samples"], 1):
        duration = sample["duration"]
        
        # Filter by duration
        if duration < MIN_DURATION or duration > MAX_DURATION:
            continue
        
        # Source and target paths
        source_path = BASE_DIR / sample["audio_path"]
        if not source_path.exists():
            continue
        
        # New filename
        audio_filename = f"hindi_tts_{valid_samples:05d}.wav"
        target_path = audio_dir / audio_filename
        
        # Convert audio
        convert_audio_format(source_path, target_path)
        
        # Add to training list
        train_list.append({
            "audio_path": str(target_path.relative_to(SOVITS_DIR)),
            "text": sample["text"],
            "speaker": sample.get("speaker", "SPEAKER_01")
        })
        
        valid_samples += 1
        if i % 50 == 0:
            print(f"   Processed {i}/{len(manifest['samples'])} samples...")
    
    print(f"\n✅ Converted {valid_samples} valid samples")
    
    # Save training list
    list_file = DATASET_DIR / "train.list"
    with open(list_file, "w", encoding="utf-8") as f:
        for item in train_list:
            # Format: audio_path|speaker|text
            f.write(f"{item['audio_path']}|{item['speaker']}|{item['text']}\n")
    
    print(f"📝 Training list saved: {list_file}")
    return True

def create_training_config():
    """Create training configuration for Mac M1"""
    
    config = {
        "train": {
            "log_interval": 100,
            "eval_interval": 500,
            "seed": 1234,
            "epochs": 100,
            "learning_rate": 0.0001,
            "betas": [0.8, 0.99],
            "eps": 1e-9,
            "batch_size": 8,  # Adjust based on M1 memory
            "accumulation_steps": 2,
            "fp16_run": False,  # M1 MPS doesn't support fp16 well
            "device": "mps"  # Use Metal Performance Shaders
        },
        "data": {
            "training_files": str(DATASET_DIR / "train.list"),
            "max_wav_value": 32768.0,
            "sampling_rate": SAMPLE_RATE,
            "filter_length": 2048,
            "hop_length": 512,
            "win_length": 2048,
            "n_mel_channels": 128,
            "mel_fmin": 0.0,
            "mel_fmax": None
        },
        "model": {
            "inter_channels": 192,
            "hidden_channels": 192,
            "filter_channels": 768,
            "n_heads": 2,
            "n_layers": 6,
            "kernel_size": 3,
            "p_dropout": 0.1,
            "resblock": "1",
            "resblock_kernel_sizes": [3, 7, 11],
            "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
            "upsample_rates": [8, 8, 2, 2],
            "upsample_initial_channel": 512,
            "upsample_kernel_sizes": [16, 16, 4, 4],
            "use_spectral_norm": False
        }
    }
    
    config_file = DATASET_DIR / "config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"⚙️  Config saved: {config_file}")
    return config_file

def print_training_instructions():
    """Print instructions to start training"""
    
    print("\n" + "="*70)
    print("🎯 Dataset Ready for Training!")
    print("="*70)
    
    print("\n📋 Next Steps:")
    print("\n1. Navigate to GPT-SoVITS directory:")
    print(f"   cd {SOVITS_DIR}")
    
    print("\n2. Start training with MPS (Mac GPU) acceleration:")
    print("   python3 GPT_SoVITS/s1_train.py \\")
    print(f"     --config_path {DATASET_DIR / 'config.json'} \\")
    print(f"     --model_name hindi_tts \\")
    print("     --device mps")
    
    print("\n3. Monitor training:")
    print("   - Checkpoints will be saved in: GPT-SoVITS/logs/")
    print("   - Training time: ~2-3 hours on M1 Mac")
    print("   - Watch terminal for loss values")
    
    print("\n💡 Tips for Mac M1:")
    print("   • Keep batch_size=8 (adjust if memory issues)")
    print("   • Close other apps to free up RAM")
    print("   • Laptop should be plugged in")
    print("   • Temperature monitoring: sudo powermetrics --samplers smc")
    
    print("\n📊 Expected Results:")
    print("   • Loss should decrease steadily")
    print("   • Good results after ~50-70 epochs")
    print("   • Best checkpoint auto-saved")
    
    print("\n" + "="*70 + "\n")

def main():
    print("="*70)
    print("🎤 GPT-SoVITS Training Setup for Mac M1")
    print("="*70)
    
    # Check if GPT-SoVITS is installed
    if not check_gpt_sovits_installed():
        return
    
    # Prepare dataset
    if not prepare_dataset():
        return
    
    # Create config
    create_training_config()
    
    # Print instructions
    print_training_instructions()

if __name__ == "__main__":
    main()
