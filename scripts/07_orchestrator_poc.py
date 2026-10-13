"""
07_orchestrator_poc.py
----------------------
Master Orchestrator — Live Terminal Demo for Mid-Sem Evaluation.

Two-agent pipeline:
  Agent 01 — Script Analyst  : Raw Hindi story lega, narrator vs character
                                dialogue turns identify karega.
  Agent 02 — Narrative Director: Har turn ka acoustic profile predict karega
                                 [EMOTION | PACE | PITCH | STYLE].

Usage:
    python3 scripts/07_orchestrator_poc.py
    python3 scripts/07_orchestrator_poc.py --story "custom kahani text here"
    python3 scripts/07_orchestrator_poc.py --file path/to/story.txt

Dependencies:
    pip3 install openai python-dotenv
"""

import argparse
import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

# ── Load API key ──────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not set. .env file mein daalo: GROQ_API_KEY=gsk_xxxx"
    )

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"

# ── Default demo story ────────────────────────────────────────────────────────
DEFAULT_STORY = """
एक घने जंगल में एक छोटा शेर का बच्चा रहता था। अचानक शाम को जोर से बिजली कड़की और तेज बारिश होने लगी।
शेर का बच्चा कांपने लगा और उसने अपनी मां से फुसफुसाकर कहा, "मां, मुझे बहुत डर लग रहा है!"
मां शेरनी ने उसे सहलाते हुए प्यार से कहा, "डरो मत मेरे बच्चे, जब तक मैं तुम्हारे साथ हूं, कोई तुम्हें नुकसान नहीं पहुंचा सकता।"
"""

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 01 — Script Analyst
# ─────────────────────────────────────────────────────────────────────────────

AGENT_01_SYSTEM = """
You are Agent 01 — Script Analyst for a Hindi TTS (Text-to-Speech) system.

Your job: Analyze a Hindi story and split it into structured "turns".
Each turn is either:
  - "narrator"   : descriptive text, sets the scene
  - "character"  : direct speech by a character

Return ONLY a valid JSON array. Each element must have:
{
  "turn_id": <integer starting from 1>,
  "type": "narrator" | "character",
  "speaker": "Narrator" | "<Character Name in English>",
  "text": "<exact Hindi text of this turn>"
}

Rules:
- Direct speech (dialogue between quotes) = character turn
- Everything else = narrator turn
- Keep the original Hindi text exactly as given
- Do not add any explanation outside the JSON array
"""


def run_agent_01(story: str) -> list[dict]:
    """Agent 01: Split story into narrator/character turns."""
    print("\n" + "═" * 60)
    print("  AGENT 01 — Script Analyst")
    print("═" * 60)
    print("[*] Story ko turns mein split kar raha hoon...\n")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": AGENT_01_SYSTEM},
            {"role": "user",   "content": f"Hindi Story:\n{story}"},
        ],
        temperature=0.1,
    )

    content = response.choices[0].message.content
    json_match = re.search(r'\[.*\]', content, re.DOTALL)
    if not json_match:
        print("[-] Agent 01: JSON parse failed. Raw output:")
        print(content)
        return []

    turns = json.loads(json_match.group())

    for turn in turns:
        tag = "🎙️ NARRATOR" if turn["type"] == "narrator" else f"💬 {turn['speaker'].upper()}"
        print(f"  Turn {turn['turn_id']:02d} [{tag}]")
        print(f"  {turn['text']}\n")

    print(f"[+] Agent 01 complete: {len(turns)} turns identified.")
    return turns


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 02 — Narrative Director
# ─────────────────────────────────────────────────────────────────────────────

AGENT_02_SYSTEM = """
You are Agent 02 — Narrative Director for a Hindi TTS (Text-to-Speech) system.

Your job: Given a list of story turns (narrator + character dialogue), assign
precise acoustic/emotional parameters to each turn for expressive TTS synthesis.

Return ONLY a valid JSON object with key "narrative_turns" containing an array.
Each element must have:
{
  "turn_id": <integer>,
  "speaker": "<speaker name>",
  "text": "<original Hindi text>",
  "emotion_tag": "Fear | Anger | Joy | Sadness | Surprise | Comforting | Dramatic/Scary | Neutral",
  "acoustic_cues": {
    "volume": "Low | Normal | High",
    "pace": "Slow | Normal | Fast",
    "pitch": "Low | Normal | High"
  },
  "style_prompt": "<1 sentence English instruction for TTS voice actor>"
}

Rules:
- Consider full story context when deciding parameters
- Narrator turns during action/suspense = Dramatic/Scary
- Character turns must reflect their emotional state
- Do not add any explanation outside the JSON object
"""


def run_agent_02(turns: list[dict]) -> list[dict]:
    """Agent 02: Assign acoustic parameters to each turn."""
    print("\n" + "═" * 60)
    print("  AGENT 02 — Narrative Director")
    print("═" * 60)
    print("[*] Har turn ka acoustic profile bana raha hoon...\n")

    turns_json = json.dumps(turns, ensure_ascii=False, indent=2)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": AGENT_02_SYSTEM},
            {"role": "user",   "content": f"Story Turns:\n{turns_json}"},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if not json_match:
        print("[-] Agent 02: JSON parse failed. Raw output:")
        print(content)
        return []

    result = json.loads(json_match.group())
    directed = result.get("narrative_turns", result) if isinstance(result, dict) else result

    # ── Print formatted output ────────────────────────────────────────────────
    EMOTION_EMOJI = {
        "Fear": "😨", "Anger": "😡", "Joy": "😄", "Sadness": "😢",
        "Surprise": "😲", "Comforting": "🤗", "Dramatic/Scary": "⚡",
        "Whispering": "🤫", "Neutral": "😐",
    }

    for turn in directed:
        cues = turn.get("acoustic_cues", {})
        emotion = turn.get("emotion_tag", "Neutral")
        emoji = EMOTION_EMOJI.get(emotion, "🎭")
        print(f"  ┌─ Turn {turn['turn_id']:02d} [{turn['speaker']}]")
        print(f"  │  Text    : {turn['text'][:70]}{'...' if len(turn['text']) > 70 else ''}")
        print(f"  │  Emotion : {emoji} {emotion}")
        print(f"  │  Volume  : {cues.get('volume','?')}  |  Pace: {cues.get('pace','?')}  |  Pitch: {cues.get('pitch','?')}")
        print(f"  └─ Style   : {turn.get('style_prompt', '?')}\n")

    print(f"[+] Agent 02 complete: {len(directed)} turns directed.")
    return directed


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────

def save_output(directed_turns: list[dict], story_text: str) -> None:
    """Save final orchestrator output to JSON."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(base_dir, "..", "data", "orchestrator_output.json")

    output = {
        "story_preview": story_text[:200] + "..." if len(story_text) > 200 else story_text,
        "total_turns": len(directed_turns),
        "turns": directed_turns,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Output saved: {os.path.abspath(out_path)}")


def main():
    parser = argparse.ArgumentParser(description="Hindi TTS Orchestrator POC")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--story", type=str, help="Hindi story text directly")
    group.add_argument("--file",  type=str, help="Path to .txt file with Hindi story")
    args = parser.parse_args()

    # Load story
    if args.story:
        story = args.story
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            story = f.read()
    else:
        story = DEFAULT_STORY

    print("\n" + "═" * 60)
    print("  HINDI TTS — MASTER ORCHESTRATOR POC")
    print("  Mid-Sem Demo | Agents 01 + 02")
    print("═" * 60)
    print(f"\n[*] Story loaded ({len(story)} chars)\n")

    # Run pipeline
    turns    = run_agent_01(story)
    if not turns:
        print("[-] Agent 01 failed. Exiting.")
        return

    directed = run_agent_02(turns)
    if not directed:
        print("[-] Agent 02 failed. Exiting.")
        return

    save_output(directed, story)

    print("\n" + "═" * 60)
    print(f"  ✅ PIPELINE COMPLETE")
    print(f"  Total turns   : {len(directed)}")
    print(f"  Emotions found: {len(set(t.get('emotion') for t in directed))}")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
