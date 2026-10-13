"""
01_scrape_youtube.py
--------------------
Downloads Hindi audiobook / kahani videos from YouTube and saves them
as 16kHz mono WAV files into data/01_raw_audio/.

Usage:
    python scripts/01_scrape_youtube.py

Dependencies:
    yt-dlp, ffmpeg (system install)
"""

import os
import yt_dlp

# ── Output folder ─────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "01_raw_audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Dataset URLs ──────────────────────────────────────────────────────────────
# Note: URLs marked [OK] were confirmed downloaded. 3 unavailable ones replaced
# with Ssoftoons Kahaniya videos (Feb 2024) from same channel family.
YOUTUBE_URLS = [
    # ✅ Already downloaded (keep these)
    "https://youtu.be/DJpmuUT0liI",  # गर्मियों की दुल्हन
    "https://youtu.be/l67JebGFskc",  # बुद्धू राम की ट्रेन यात्रा

    # 🔄 Replacements for the 3 unavailable videos (Ssoftoons Kahaniya, 2024)
    "https://www.youtube.com/watch?v=_oiG0s5KTv0",  # नींद का कमाल
    "https://www.youtube.com/watch?v=sxEAM_3XTGU",  # डबल शादी का भोज
    "https://www.youtube.com/watch?v=hZ5oVNu3MoA",  # Hindi Kahaniya Comedy
]


def download_hindi_audio(urls: list[str], output_path: str) -> None:
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                # Step 1: extract audio as WAV
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            },
        ],
        # Step 2: resample to 16kHz mono (optimal for Whisper & TTS models)
        "postprocessor_args": [
            "-ar", "16000",  # 16 kHz sample rate
            "-ac", "1",      # mono channel
        ],
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "ignoreerrors": True,   # skip unavailable videos without crashing
        "noplaylist": False,    # allow playlists if a playlist URL is added
        "nooverwrites": True,   # don't re-download files that already exist
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"[*] Downloading {len(urls)} video(s) into: {os.path.abspath(output_path)}")
        ydl.download(urls)
        print("[+] All downloads completed!")


if __name__ == "__main__":
    download_hindi_audio(YOUTUBE_URLS, OUTPUT_DIR)
