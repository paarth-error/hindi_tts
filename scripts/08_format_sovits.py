import os
import json

MANIFEST_PATH = os.path.join("..", "data", "dataset_manifest.json")
OUTPUT_LIST_PATH = os.path.join("..", "data", "sovits_filelist.txt")

def create_sovits_filelist():
    if not os.path.exists(MANIFEST_PATH):
        print("[-] dataset_manifest.json nahi mila!")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    for item in data:
        # Relate path or absolute path to audio chunk
        audio_path = item.get("audio_path", "")
        speaker = item.get("speaker", "Speaker_00")
        text = item.get("text", "").strip()

        if not audio_path or not text:
            continue

        abs_audio_path = os.path.abspath(os.path.join("..", "data", "03_diarized_segments", audio_path))
        # Format: audio_path|speaker_name|language|text
        lines.append(f"{abs_audio_path}|{speaker}|HI|{text}")

    with open(OUTPUT_LIST_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[+] GPT-SoVITS filelist created successfully!")
    print(f"[+] Total samples ready for training: {len(lines)}")
    print(f"[+] File saved at: {OUTPUT_LIST_PATH}")

if __name__ == "__main__":
    create_sovits_filelist()