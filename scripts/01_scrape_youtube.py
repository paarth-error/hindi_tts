"""
01_scrape_youtube.py
--------------------
Downloads Hindi kahani / audiobook videos from YouTube as 16kHz mono WAV.
Supports individual URLs, playlist URLs, and a channel's latest videos.

Target: 20-30 videos = ~4-6 hours clean audio for production TTS training.

Usage:
    python3 scripts/01_scrape_youtube.py

Dependencies:
    yt-dlp, ffmpeg (brew install ffmpeg)
"""

import os
import yt_dlp

# ── Output folder ─────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "01_raw_audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Dataset Sources ───────────────────────────────────────────────────────────
# Strategy: Use playlists — automatically gets N videos from best channels.
# Each playlist set to download 10 videos = ~30 videos total across 3 playlists.
#
# Best channels for Hindi TTS:
#   - Clear single narrator voice
#   - Minimal overlapping speech
#   - Good Hindi pronunciation (Devanagari)
#   - Consistent audio quality

YOUTUBE_SOURCES = [
    # ── Confirmed working individual videos ───────────────────────────────────
    "https://youtu.be/DJpmuUT0liI",   # गर्मियों की दुल्हन
    "https://youtu.be/l67JebGFskc",   # बुद्धू राम की ट्रेन यात्रा

    # ── Playlists (add playlist URLs below) ───────────────────────────────────
    # Ssoftoons Hindi — large playlist of Hindi kahaniya
    "https://youtube.com/playlist?list=PLhSN612TBIy-4dAzIZrNAsFwD1ZHgXUO2&si=XzHdO3zTJoRc1fvT",

    # Moral Stories Hindi
    "https://youtube.com/playlist?list=PLGYShKhywmbrE2JhGnahfVHq16ufnG-2r&si=nFADXVU072QOFGkP",

    # Kahani Junction
    # "https://www.youtube.com/playlist?list=PLxxxxxxx",
]

# ── How many videos to pull from each playlist ────────────────────────────────
PLAYLIST_LIMIT = 10   # 3 playlists × 10 = 30 videos total

# ── Minimum video duration to download (seconds) ─────────────────────────────
# Skip very short clips (< 3 min) — not useful for TTS
MIN_DURATION = 180   # 3 minutes

# ── Maximum video duration (seconds) ─────────────────────────────────────────
# Skip very long videos (> 30 min) — too much background variation
MAX_DURATION = 1800  # 30 minutes


def download_hindi_audio(urls: list[str], output_path: str) -> None:
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            },
        ],
        # 16kHz mono — optimal for Whisper + TTS training
        "postprocessor_args": [
            "-ar", "16000",
            "-ac", "1",
        ],
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "ignoreerrors":  True,   # skip unavailable videos
        "nooverwrites":  True,   # skip already downloaded files
        "playlistend":   PLAYLIST_LIMIT,

        # Filter by duration
        "match_filter": yt_dlp.utils.match_filter_func(
            f"duration >= {MIN_DURATION} & duration <= {MAX_DURATION}"
        ),

        # Progress display
        "quiet":        False,
        "no_warnings":  False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"[*] Downloading from {len(urls)} source(s)...")
        print(f"[*] Output: {os.path.abspath(output_path)}")
        print(f"[*] Duration filter: {MIN_DURATION//60}-{MAX_DURATION//60} minutes\n")
        ydl.download(urls)

    # Count downloaded files
    wav_files = [f for f in os.listdir(output_path) if f.endswith(".wav")]
    print(f"\n[+] Total WAV files in folder: {len(wav_files)}")
    print("[+] Download complete!")


if __name__ == "__main__":
    download_hindi_audio(YOUTUBE_SOURCES, OUTPUT_DIR)
