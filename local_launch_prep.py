#!/usr/bin/env python3
"""
local_launch_prep.py
Stages pre-launch and launch-day copy packages into Master Sheet 'Social_Vault'.
"""

import os
import sys
import gspread

SHEET_ID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"
SA_PATH = "/Users/jameswilliams/murk-runners/service_account.json"
TARGET_TAB = "Social_Vault"

STAGED_PACKAGES = [
    # Wave 1: Thursday T-48h (X / Twitter)
    [
        "2026-08-13",
        "X (Twitter)",
        "T-48h Teaser",
        "Portland. 1951. A detective who hears things that aren't there — or are they?\n\nDead Signal drops this Saturday, August 15. Produced in binaural 3D spatial audio. Grab your headphones and subscribe now so you don't miss the drop. 🎧 🦅 #DeadSignal #AudioDrama #IndieAudio #Noir",
        "STAGED"
    ],
    # Wave 1: Thursday T-48h (LinkedIn)
    [
        "2026-08-13",
        "LinkedIn",
        "T-48h Infrastructure & Tech",
        "Designing audio drama for modern listeners requires treating sound design as a physical environment.\n\nOur debut production 'Dead Signal' drops this Saturday, August 15. Mixed entirely in binaural 3D spatial audio, it puts the listener directly inside a 1951 Portland detective office.\n\nNo label. No network. Built independently right here in Portland, Oregon. Subscribe on Apple Podcasts or Spotify ahead of Saturday's release: https://murk.audio/dead-signal\n\n#AudioProduction #SpatialAudio #IndieStudio #DeadSignal #SystemsDesign",
        "STAGED"
    ],
    # Wave 2: Friday T-24h (Bluesky / Mastodon)
    [
        "2026-08-14",
        "Bluesky / Mastodon",
        "T-24h Countdown",
        "The door was never locked. Releasing in 24 hours.\n\nDead Signal — Saturday, August 15.\nWritten & produced by The Murk Audio LLC in Portland, OR.\n\nPre-add or listen to the official trailer now at https://murk.audio/ 🦅",
        "STAGED"
    ],
    # Wave 3: Saturday Launch Day (All Channels)
    [
        "2026-08-15",
        "All Platforms",
        "T-0 Launch Drop",
        "DEAD SIGNAL IS LIVE. 🎧\n\n20 minutes of immersive noir audio fiction produced in binaural 3D spatial audio. Headphones on. Lights off.\n\nStream now on Apple Podcasts, Spotify, or directly at https://murk.audio/dead-signal\n\n#DeadSignal #AudioDrama #Noir #PortlandAudio #TheMurk",
        "STAGED"
    ]
]

def main():
    print("🦅 MARIE ENGINE — PRE-LAUNCH STAGING ROUTINE")
    if not os.path.exists(SA_PATH):
        print(f"❌ Error: Service account missing at {SA_PATH}")
        sys.exit(1)
        
    try:
        gc = gspread.service_account(filename=SA_PATH)
        sh = gc.open_by_key(SHEET_ID)
        vault = sh.worksheet(TARGET_TAB)
        
        print(f"🔓 Connected to Master Sheet ID: {SHEET_ID}")
        print(f"📊 Target Tab: {TARGET_TAB}")
        
        vault.append_rows(STAGED_PACKAGES)
        print(f"✅ Successfully staged {len(STAGED_PACKAGES)} launch packages to '{TARGET_TAB}'!")
        
    except Exception as e:
        print(f"💥 Staging failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
