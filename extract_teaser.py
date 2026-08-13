#!/usr/bin/env python3
"""
extract_teaser.py
Precision clip extraction engine for 'Dead Signal' master audio.
Usage: python3 extract_teaser.py <output_filename> <start_time> [duration_seconds]
Example: python3 extract_teaser.py teaser_01_ambient 01:45 15
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = "/Users/jameswilliams/murk-runners/content/dead-signal"
MASTER_DIR = os.path.join(BASE_DIR, "master")
STAGING_DIR = os.path.join(BASE_DIR, "staging", "audiograms")
os.makedirs(STAGING_DIR, exist_ok=True)

ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"

masters = [f for f in os.listdir(MASTER_DIR) if f.endswith((".wav", ".mp3", ".flac", ".m4a"))]
if not masters:
    print(f"❌ Error: No master file found in {MASTER_DIR}")
    sys.exit(1)

target_file = os.path.join(MASTER_DIR, masters[0])

def main():
    if len(sys.argv) < 3:
        print("\n🎙️ Precision Audiogram Extraction Engine")
        print("--------------------------------------------------")
        print("Usage:   python3 extract_teaser.py <clip_name> <start_time> [duration_in_seconds]")
        print("Example: python3 extract_teaser.py teaser_01_ambient 01:15 15")
        print("Example: python3 extract_teaser.py teaser_02_hook 04:22 15")
        print("--------------------------------------------------\n")
        sys.exit(1)

    clip_name = sys.argv[1].replace(".mp3", "")
    start_time = sys.argv[2]
    duration = sys.argv[3] if len(sys.argv) > 3 else "15"
    
    output_path = os.path.join(STAGING_DIR, f"{clip_name}.mp3")

    cmd = [
        ffmpeg_bin, "-y",
        "-ss", start_time,
        "-i", target_file,
        "-t", str(duration),
        "-acodec", "libmp3lame",
        "-ab", "192k",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Successfully rendered [{clip_name}.mp3]")
        print(f"   • Start Time : {start_time}")
        print(f"   • Duration   : {duration}s")
        print(f"   • Staged At  : {output_path}")
    except Exception as e:
        print(f"💥 Extraction failed: {e}")

if __name__ == "__main__":
    main()
