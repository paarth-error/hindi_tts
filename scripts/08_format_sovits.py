#!/usr/bin/env python3
"""
Step 8: Format dataset for different TTS training frameworks
Supports: GPT-SoVITS, Coqui XTTS, Piper
"""

import os
import json
import argparse
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
MANIFEST_PATH = BASE_DIR / "data" / "07_final" / "manifest.json"

def format_gpt_sovits(manifest_data: dict, output_dir: Path):
    """Format for GPT-SoVITS training"""
    output_file = output_dir / "sovits_filelist.txt"
    
    lines = []
    for item in manifest_data["samples"]:
        audio_path = BASE_DIR / item["audio_path"]
        speaker = item.get("speaker", "SPEAKER_00")
        text = item["text"].strip()
        
        if not audio_path.exists() or not text:
            continue
        
        # Format: audio_path|speaker_name|language|text
        lines.append(f"{audio_path.absolute()}|{speaker}|HI|{text}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"\n✅ GPT-SoVITS format created: {output_file}")
    print(f"   Total samples: {len(lines)}")
    return output_file

def format_coqui_xtts(manifest_data: dict, output_dir: Path):
    """Format for Coqui TTS XTTS training"""
    
    # Create metadata.csv for XTTS
    metadata_file = output_dir / "metadata.csv"
    
    lines = ["audio_file|text|speaker_name"]
    for item in manifest_data["samples"]:
        audio_path = BASE_DIR / item["audio_path"]
        speaker = item.get("speaker", "SPEAKER_00")
        text = item["text"].strip()
        
        if not audio_path.exists() or not text:
            continue
        
        # XTTS format: filename|text|speaker
        lines.append(f"{audio_path.absolute()}|{text}|{speaker}")
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    # Create XTTS config
    config = {
        "run_name": "hindi_tts_xtts",
        "model": "xtts",
        "audio": {
            "sample_rate": 22050,
            "max_wav_value": 32768.0
        },
        "datasets": [{
            "name": "hindi_tts",
            "path": str(output_dir.parent),
            "meta_file": "metadata.csv",
            "language": "hi"
        }],
        "training": {
            "batch_size": 4,
            "epochs": 100,
            "learning_rate": 0.0001,
            "mixed_precision": False,  # MPS doesn't support mixed precision well
            "device": "mps"
        }
    }
    
    config_file = output_dir / "xtts_config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Coqui XTTS format created:")
    print(f"   Metadata: {metadata_file}")
    print(f"   Config: {config_file}")
    print(f"   Total samples: {len(lines) - 1}")
    return metadata_file

def format_piper(manifest_data: dict, output_dir: Path):
    """Format for Piper TTS training"""
    
    # Piper uses a simpler format
    metadata_file = output_dir / "piper_metadata.csv"
    
    lines = []
    for item in manifest_data["samples"]:
        audio_path = BASE_DIR / item["audio_path"]
        text = item["text"].strip()
        
        if not audio_path.exists() or not text:
            continue
        
        # Piper format: filename|text
        relative_path = audio_path.relative_to(BASE_DIR)
        lines.append(f"{relative_path}|{text}")
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"\n✅ Piper TTS format created: {metadata_file}")
    print(f"   Total samples: {len(lines)}")
    return metadata_file

def show_stats(manifest_data: dict):
    """Show dataset statistics"""
    
    samples = manifest_data["samples"]
    total_duration = sum(s["duration"] for s in samples)
    speakers = set(s.get("speaker", "unknown") for s in samples)
    
    print("\n" + "="*60)
    print("📊 Dataset Statistics")
    print("="*60)
    print(f"Total samples: {len(samples)}")
    print(f"Total duration: {total_duration/60:.1f} minutes ({total_duration:.1f} seconds)")
    print(f"Average duration: {total_duration/len(samples):.2f} seconds")
    print(f"Speakers: {len(speakers)}")
    print(f"Speaker IDs: {', '.join(sorted(speakers))}")
    
    # Duration distribution
    durations = [s["duration"] for s in samples]
    short = sum(1 for d in durations if d < 3)
    medium = sum(1 for d in durations if 3 <= d < 10)
    long = sum(1 for d in durations if d >= 10)
    
    print(f"\nDuration distribution:")
    print(f"  < 3 seconds: {short} samples")
    print(f"  3-10 seconds: {medium} samples")
    print(f"  >= 10 seconds: {long} samples")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="Format Hindi TTS dataset for training"
    )
    parser.add_argument(
        "--format",
        choices=["sovits", "xtts", "piper", "all"],
        default="sovits",
        help="Output format (default: sovits)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show dataset statistics"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🎤 Format Dataset for TTS Training")
    print("="*60)
    
    # Load manifest
    if not MANIFEST_PATH.exists():
        print(f"\n❌ Manifest not found: {MANIFEST_PATH}")
        print("   Run scripts 01-06 first!")
        return
    
    print(f"\n📂 Loading manifest: {MANIFEST_PATH}")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    
    # Show stats if requested
    if args.stats:
        show_stats(manifest_data)
        return
    
    # Create output directory
    output_dir = MANIFEST_PATH.parent
    
    # Format based on selection
    if args.format == "sovits" or args.format == "all":
        format_gpt_sovits(manifest_data, output_dir)
    
    if args.format == "xtts" or args.format == "all":
        format_coqui_xtts(manifest_data, output_dir)
    
    if args.format == "piper" or args.format == "all":
        format_piper(manifest_data, output_dir)
    
    print("\n💡 Next steps:")
    if args.format == "sovits" or args.format == "all":
        print("   GPT-SoVITS: python3 scripts/09_train_gpt_sovits_mac.py")
    if args.format == "xtts" or args.format == "all":
        print("   XTTS: tts-train --config_path data/07_final/xtts_config.json")
    if args.format == "piper" or args.format == "all":
        print("   Piper: See TRAINING_GUIDE.md for instructions")
    
    print("\n📖 Read TRAINING_GUIDE.md for detailed instructions")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()