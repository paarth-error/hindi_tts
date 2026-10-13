"""
05_llm_autotagging.py
---------------------
Groq LLM (llama-3.3-70b) se har Hindi text segment ko analyze karke
emotion, pitch, speed aur style_prompt tags add karo.

Reads  : data/metadata.csv
Writes : data/metadata_enriched.csv

Tags added per row:
    emotion      : Fear | Anger | Joy | Sadness | Surprise | Whispering | Neutral
    pitch        : Low | Medium | High
    speed        : Slow | Normal | Fast
    style_prompt : English instruction for TTS (e.g. "Whisper fearfully, low pitch")

Usage:
    python3 scripts/05_llm_autotagging.py

Setup:
    1. pip3 install openai pandas tqdm python-dotenv
    2. Groq free API key: https://console.groq.com/
    3. .env file mein daalo: GROQ_API_KEY=gsk_xxxx
"""

import json
import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

# ── Load API key from .env ────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not set.\n"
        "Groq free key banao: https://console.groq.com/\n"
        "Phir .env file mein daalo: GROQ_API_KEY=gsk_xxxx"
    )

# ── Folder paths ──────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
METADATA_INPUT  = os.path.join(BASE_DIR, "..", "data", "metadata.csv")
METADATA_OUTPUT = os.path.join(BASE_DIR, "..", "data", "metadata_enriched.csv")

# ── Groq client (OpenAI-compatible API) ──────────────────────────────────────
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

GROQ_MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
You are an expert audio director for Hindi storytelling and TTS (Text-to-Speech) systems.
Analyze the provided Hindi text segment and extract emotional prosody cues.

Return ONLY a valid JSON object with exactly these keys:
{
  "emotion": "Fear | Anger | Joy | Sadness | Surprise | Whispering | Neutral",
  "pitch": "Low | Medium | High",
  "speed": "Slow | Normal | Fast",
  "style_prompt": "A short English instruction describing how to speak this line expressively"
}

Rules:
- Choose the single best-fitting value for each key.
- style_prompt should be 1 sentence max, in English.
- Do not add any explanation outside the JSON.
"""

# ── Default fallback if API fails ─────────────────────────────────────────────
DEFAULT_TAGS = {
    "emotion":      "Neutral",
    "pitch":        "Medium",
    "speed":        "Normal",
    "style_prompt": "Speak naturally in standard Hindi",
}


def tag_hindi_text(text: str) -> dict:
    """Send one Hindi text segment to Groq and get back emotion/pitch/speed tags."""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Hindi Text: {text}"},
            ],
            temperature=0.2,
        )
        # Extract JSON from response text
        import re
        content = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return DEFAULT_TAGS.copy()
    except Exception as e:
        print(f"\n[-] API error (using defaults): {e}")
        return DEFAULT_TAGS.copy()


def process_autotagging() -> None:
    if not os.path.exists(METADATA_INPUT):
        print(f"[-] metadata.csv nahi mili: {os.path.abspath(METADATA_INPUT)}")
        print("    Pehle 04_transcribe_whisper.py run karo.")
        return

    df = pd.read_csv(METADATA_INPUT)
    print(f"[*] {len(df)} segments ko LLM se tag kiya jayega...\n")

    emotions, pitches, speeds, style_prompts = [], [], [], []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Tagging"):
        text = str(row.get("text", "")).strip()

        if not text:
            emotions.append(DEFAULT_TAGS["emotion"])
            pitches.append(DEFAULT_TAGS["pitch"])
            speeds.append(DEFAULT_TAGS["speed"])
            style_prompts.append(DEFAULT_TAGS["style_prompt"])
            continue

        tags = tag_hindi_text(text)
        emotions.append(tags.get("emotion",      DEFAULT_TAGS["emotion"]))
        pitches.append(tags.get("pitch",         DEFAULT_TAGS["pitch"]))
        speeds.append(tags.get("speed",          DEFAULT_TAGS["speed"]))
        style_prompts.append(tags.get("style_prompt", DEFAULT_TAGS["style_prompt"]))

    # ── Add new columns aur save karo ────────────────────────────────────────
    df["emotion"]      = emotions
    df["pitch"]        = pitches
    df["speed"]        = speeds
    df["style_prompt"] = style_prompts

    df.to_csv(METADATA_OUTPUT, index=False, encoding="utf-8-sig")
    print(f"\n[+] Auto-tagging complete! {len(df)} rows tagged.")
    print(f"[+] Enriched dataset: {os.path.abspath(METADATA_OUTPUT)}")

    # ── Quick stats ───────────────────────────────────────────────────────────
    print("\n── Emotion Distribution ──")
    print(df["emotion"].value_counts().to_string())
    print("\n── Pitch Distribution ──")
    print(df["pitch"].value_counts().to_string())
    print("\n── Speed Distribution ──")
    print(df["speed"].value_counts().to_string())


if __name__ == "__main__":
    process_autotagging()
