#!/usr/bin/env python3
"""
local_audio_ingest.py
Local Mac Mini offline processing pipeline for 'Dead Signal' master audio.
Keeps master files strictly offline in git-ignored staging directories.
"""

import os
import sys
import subprocess

BASE_DIR = "/Users/jameswilliams/murk-runners/content/dead-signal"
MASTER_DIR = os.path.join(BASE_DIR, "master")
STAGING_DIR = os.path.join(BASE_DIR, "staging")
AUDIOGRAM_DIR = os.path.join(STAGING_DIR, "audiograms")

def main():
    print("🦅 MARIE ENGINE — LOCAL OFFLINE AUDIO INGESTION PIPELINE")
    
    # Ensure local directory isolation
    os.makedirs(MASTER_DIR, exist_ok=True)
    os.makedirs(AUDIOGRAM_DIR, exist_ok=True)
    
    print(f"📁 Master Audio Target Folder : {MASTER_DIR}")
    print(f"📁 Audiogram Staging Folder   : {AUDIOGRAM_DIR}")
    
    # Find local WAV or MP3 master files
    masters = [f for f in os.listdir(MASTER_DIR) if f.endswith(('.wav', '.mp3', '.flac', '.m4a'))]
    
    if not masters:
        print("\n⚠️ No master audio file found in 'content/dead-signal/master/'.")
        print("👉 Drop your 'Dead_Signal_Full_Master.wav' into that directory to extract teaser audiograms.")
        return

    target_master = os.path.join(MASTER_DIR, masters[0])
    print(f"🎙️ Found Master File: {masters[0]}")
    
    # Example 15-second ambient teaser snippet extraction (00:00:30 to 00:00:45)
    teaser_output = os.path.join(AUDIOGRAM_DIR, "teaser_15s_ambient.mp3")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-ss", "00:00:30", "-i", target_master,
        "-t", "15", "-acodec", "libmp3lame", "-ab", "192k", teaser_output
    ]
    
    try:
        print("⚡ Extracting 15-second offline teaser clip via FFmpeg...")
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Teaser created successfully: {teaser_output}")
    except Exception as e:
        print(f"ℹ️ FFmpeg note: Install via Homebrew ('brew install ffmpeg') to generate teaser clips locally.")

if __name__ == "__main__":
    main()
