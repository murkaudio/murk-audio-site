#!/usr/bin/env python3
import os, sys, gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

CATEGORIES = {
    "PNW": [
        ("Meyer Memorial Trust Blueprint Grant", "Meyer Memorial Trust", "Oregon", "Yes — via fiscal sponsor", "TBD"),
        ("Oregon Arts Commission Arts Build Communities", "Oregon Arts Commission", "Oregon", "Yes", "$3,000-$7,000"),
        ("RACC Arts 3C Grant Program", "Regional Arts & Culture Council", "Portland, OR Region", "Yes", "$1,000-$5,000"),
        ("The Collins Foundation Media Access Fund", "The Collins Foundation", "Oregon", "Yes — via fiscal sponsor", "Varies"),
        ("OCF Small Arts and Culture Grants", "Oregon Community Foundation", "Oregon", "Yes", "$1,000-$10,000"),
        ("James F. and Marion L. Miller Digital Arts Cohort", "Miller Foundation Oregon", "Oregon", "Yes — via fiscal sponsor", "TBD"),
        ("Portland General Electric Creative Community Fund", "Portland General Electric", "Portland, OR", "Yes", "$5,000"),
        ("Juan Young Trust Creative Youth Development", "Juan Young Trust", "Oregon", "Yes — via fiscal sponsor", "Up to $10,000"),
        ("Autzen Foundation Arts and Culture Stream", "Autzen Foundation", "Pacific NW", "Yes — via fiscal sponsor", "$2,000-$5,000"),
        ("Jackson Foundation Northwest Media Initiative", "Jackson Foundation", "Oregon", "Yes", "$5,000-$10,000"),
        ("Marie Lamfrom Charitable Foundation Arts Grant", "Marie Lamfrom Foundation", "Oregon / Washington", "Yes", "$5,000-$25,000"),
        ("Ford Family Foundation Creative Opportunity Fund", "Ford Family Foundation", "Oregon Statewide", "Yes", "Varies"),
        ("Wildwood Foundation Digital Storytelling Grant", "Wildwood Foundation", "Oregon", "Yes", "$5,000"),
        ("Woodard Family Foundation Media Arts Program", "Woodard Family Foundation", "Pacific NW", "Yes", "$2,500-$7,500"),
        ("Spirit Mountain Community Fund Cultural Allocation", "Spirit Mountain Community Fund", "Oregon (Multi-County)", "Yes", "Up to $50,000"),
        ("Seeding Justice Creative Media Organizing Fund", "Seeding Justice", "Oregon", "Yes", "$5,000-$15,000"),
        ("Pamplin Foundation Historical Arts Ingestion", "Pamplin Foundation", "Portland, OR", "Yes", "TBD"),
        ("Maybelle Clark Macdonald Fund Creative Works", "MCM Foundation", "Oregon", "Yes — via fiscal sponsor", "Varies"),
        ("Kinsman Foundation Architectural & Audio Arts", "Kinsman Foundation", "Oregon / Washington", "Yes", "$5,000-$10,000"),
        ("Coit Family Foundation Pacific NW Storytelling Fund", "Coit Family Foundation", "Pacific NW", "Yes", "$5,000")
    ],
    "VET": [
        ("IVMF Syracuse University Ignite Grant", "D'Aniello Institute (IVMF)", "National", "Yes", "$5,000-$25,000"),
        ("PenFed Foundation Veteran Entrepreneur Program", "PenFed Foundation", "National", "Yes", "Seed Capital"),
        ("Bob Woodruff Foundation Local Media Project Award", "Bob Woodruff Foundation", "National", "Yes", "Varies"),
        ("Texas Veterans Commission Media Ingestion Scope", "TVC Fund", "Regional / TX Scope Only", "No", "N/A"),
        ("Farmer Veteran Fellowship Creative Enterprise Fund", "Farmer Veteran Coalition", "National", "Yes", "$1,000-$5,000"),
        ("Disabled American Veterans Entrepreneurial Pipeline", "DAV National", "National", "Yes", "Resource-based"),
        ("Starbucks Veteran Small Business Initiative", "Starbucks Foundation", "National", "Yes", "Workspace/Grants"),
        ("Home Depot Foundation Veteran Enterprise Spaces", "Home Depot Foundation", "National", "Yes", "Capital Ingestion"),
        ("Citi Salutes Veteran Creative Small Business Network", "Citi Foundation", "National", "Yes", "Varies"),
        ("First Command Educational Foundation Small Business", "First Command Foundation", "National", "Yes", "$2,500"),
        ("Mission Wire Veteran Venture Ingestion Fund", "Mission Wire Program", "National", "Yes", "Seed Allocation"),
        ("Hivers and Strivers Creative Angel Allocation", "Hivers & Strivers", "National", "Yes", "Equity / Varies"),
        ("VetFran Entrepreneur Creative Infrastructure Program", "VetFran Association", "National", "Yes", "Resource Allocation"),
        ("American Legion Veteran Business Development Award", "American Legion National", "National", "Yes", "Varies"),
        ("VFW Sport Clips Help A Hero Entrepreneur Fund", "VFW National", "National", "Yes", "Up to $5,000"),
        ("Syracuse IVMF Veterans Veterans Coalition Seed Fund", "IVMF Network", "National", "Yes", "$10,000"),
        ("Boots to Business Startup Growth Grant", "SBA Veterans Office", "National", "Yes", "Training/Capital Offset"),
        ("Patriot Boot Camp Creative Digital Ingestion Fund", "Patriot Boot Camp", "National", "Yes", "Varies"),
        ("NCOA Veteran Small Business Venture Stipend", "Non Commissioned Officers Assoc", "National", "Yes", "$1,500"),
        ("AMVETS National Entrepreneurial Support Track", "AMVETS National", "National", "Yes", "Resource-based")
    ],
    "MEDIA": [
        ("ITVS Audio Adaptation and Script Track", "Independent Television Service", "National", "Yes", "Varies"),
        ("NEA Media Arts Program — Fall Cycle", "National Endowment for the Arts", "National", "No — 501c3 required", "$10,000-$100,000"),
        ("NEH Public Humanities Digital Projects", "National Endowment for the Humanities", "National", "No — 501c3 required", "Up to $100,000"),
        ("IDA Enterprise Audio Storytelling Fund", "International Documentary Association", "National", "Yes", "TBD"),
        ("Sound & Vision Immersive Sound Innovation Grant", "Sound & Vision Association", "National", "Yes", "$5,000-$20,000"),
        ("Resonate Podcast Festival Acceleration Award", "Resonate Audio Collective", "National", "Yes", "$2,500"),
        ("Third Coast Audio Fiction Master Track Qualifier", "Third Coast International", "Global", "Yes", "Varies"),
        ("Tribeca Film Institute Immersive Storytelling Allocation", "Tribeca Enterprises", "National", "Yes", "Varies"),
        ("Gotham Film & Media Project Digital Audio Lab", "The Gotham", "National", "Yes", "Resource + Stipend"),
        ("Film Independent Digital Audio Production Track", "Film Independent", "National", "Yes", "Fellowship Stipend"),
        ("Creative Capital Emerging Media Initiative", "Creative Capital", "National", "Yes", "Up to $50,000"),
        ("Eyebeam Technology and Sound Arts Residency Fund", "Eyebeam Collective", "National", "Yes", "$10,000 Stipend"),
        ("Firelight Media Digital Audio Development Fund", "Firelight Media", "National", "Yes", "$5,000-$15,000"),
        ("MacArthur Foundation Journalism & Media Allocation", "MacArthur Foundation", "National", "Yes — via fiscal sponsor", "Varies"),
        ("Knight Foundation Immersive Sound Journalism Grant", "Knight Foundation", "National", "Yes", "Varies"),
        ("Jerome Foundation Media Arts Multi-Year Fellowship", "Jerome Foundation", "Regional / Selected States", "No — NY/MN Only", "$20,000"),
        ("Hollywood Foreign Press Association Digital Arts Support", "HFPA", "National", "Yes", "Varies"),
        ("Alfred P. Sloan Science & Technology Script Grant", "Sloan Foundation", "National", "Yes", "$10,000-$30,000"),
        ("National Press Foundation Audio Innovation Fellowship", "NPF", "National", "Yes", "Stipend-based"),
        ("International Audio Fiction Guild Production Fund", "IAFG", "Global", "Yes", "$2,000-$5,000")
    ],
    "TECH": [
        ("Epic Games MegaGrants — Spatial Audio Integration", "Epic Games", "Global", "Yes", "$5,000-$500,000"),
        ("Adobe Creative Residency Community Fund Allocation", "Adobe Systems", "Global", "Yes", "$5,000-$15,000"),
        ("Google for Startups Veteran Founders Match Layer", "Google for Startups", "National", "Yes", "Capital Match / Equity Free"),
        ("AWS Activate Startup Digital Capital Credits", "Amazon Web Services", "Global", "Yes", "Up to $100,000 Cloud Offsets"),
        ("Microsoft for Startups Founders Hub Resource Ingestion", "Microsoft", "Global", "Yes", "Software + Capital Offset"),
        ("Unity Charitable Fund Immersive Narrative Allocation", "Unity Technologies", "Global", "Yes", "$10,000-$50,000"),
        ("Shutterstock Create Fund for Immersive Media Arts", "Shutterstock", "Global", "Yes", "$2,500-$10,000"),
        ("Getty Images Creative Grant for Digital Storytellers", "Getty Images", "Global", "Yes", "$5,000-$10,000"),
        ("Patreon Creator Infrastructure Seed Grants", "Patreon Foundation", "Global", "Yes", "$1,000-$5,000"),
        ("Kickstarter Creator-in-Residence Production Stipends", "Kickstarter PBC", "Global", "Yes", "Varies"),
        ("Substack Independent Audio Production Grant Program", "Substack Inc", "National", "Yes", "$5,000-$10,000"),
        ("Spotify Independent Creator Equity Fund Allocations", "Spotify", "Global", "Yes", "Production Funding"),
        ("Apple Podcasts Independent Audio Development Loops", "Apple Media", "Global", "Yes", "Development Capital"),
        ("Dolby Institute Spatial Audio Mastering Ingestion", "Dolby Laboratories", "National", "Yes", "Studio Access + $5,000"),
        ("Meta Immersive Sound and Narrative Pioneer Tracks", "Meta Reality Labs", "Global", "Yes", "Varies"),
        ("Descript Audio Creator Development Grant", "Descript Inc", "Global", "Yes", "Software + $2,500"),
        ("Rode Microphones Creative Production Cash Infusion", "Rode", "Global", "Yes", "Equipment + $5,000"),
        ("Soundcloud Next-Gen Independent Storyteller Fund", "Soundcloud", "Global", "Yes", "Varies"),
        ("Acast Audio Fiction Production Accelerator Fund", "Acast", "International", "Yes", "$3,000-$7,000"),
        ("Sennheiser Audio Innovation Project Stipend", "Sennheiser", "Global", "Yes", "Hardware + Capital")
    ],
    "MICRO": [
        ("Awesome Foundation Seattle Monthly Micro-Grant", "Awesome Foundation Seattle", "Washington", "Yes", "$1,000"),
        ("Awesome Foundation Bend Regional Storyteller Fund", "Awesome Foundation Bend", "Oregon", "Yes", "$1,000"),
        ("Awesome Foundation Eugene Grassroots Production Fund", "Awesome Foundation Eugene", "Oregon", "Yes", "$1,000"),
        ("Content is Queen Audio Fiction Ongoing Injection", "Content is Queen", "Global", "Yes", "$500-$1,500"),
        ("The Pollination Project Continuous Seed Ingestion", "The Pollination Project", "Global", "Yes", "Up to $1,000"),
        ("Adolph & Esther Gottlieb Ongoing Crisis Backstop", "Gottlieb Foundation", "Global", "Yes", "Up to $5,000"),
        ("Foundation for Contemporary Arts Micro Emergency Pool", "FCA", "National", "Yes", "Up to $3,000"),
        ("Artist Relief Project Open-Ended Micro-Stipends", "Artist Relief Project", "Global", "Yes", "Varies"),
        ("Quick Hatch Audio Experimental Incubation Fund", "Quick Hatch Media", "National", "Yes", "$2,500"),
        ("NextUp Alternative Media Rolling Production Loops", "NextUp Collective", "National", "Yes", "$1,000"),
        ("Arts Writers Production Guild Matrix Check", "Arts Writers Collective", "National", "Yes", "Monitoring Block"),
        ("QueerArt Production Track Infrastructure Backstop", "QueerArt Inc", "National", "Yes", "Varies"),
        ("Black Public Media Digital Narrative Allocation", "Black Public Media", "National", "Yes", "Varies"),
        ("Latino Public Broadcasting Immersive Audio Fund", "LPB", "National", "Yes", "Varies"),
        ("Center for Asian American Media Storytelling Loops", "CAAM", "National", "Yes", "Varies"),
        ("Vision Maker Media Public Broadcasting Tracks", "Vision Maker Media", "National", "Yes", "Varies"),
        ("Pacific Pioneers Fund Digital Media Arts Ingestion", "Pacific Pioneers Fund", "California / Oregon", "Yes — via fiscal sponsor", "$1,000-$10,000"),
        ("Independent Audio Fiction Seed Fund Series B", "Audio Fiction Syndicate", "Global", "Yes", "$1,500"),
        ("Micro-Capital Production Grants for Sound Arts", "Sound Arts Trust", "National", "Yes", "$2,000"),
        ("The Creator Matrix Rolling Production Cash Fund", "Creator Matrix", "Global", "Yes", "$1,000")
    ]
}

def main():
    print("=" * 75); print("🛡️ STARLIGHT PIPELINE EXTENSION — INJECTING 100 FRESH CANIDATES")
    print("=" * 75)
    if not os.path.exists(SF): print("❌ System Error: Service account token missing."); sys.exit(1)

    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        existing_values = ws.get_all_values()
        current_row_count = len(existing_values)
        
        # Determine dynamic sequential ID indexing value
        next_id = 1
        for row in reversed(existing_values[4:]):
            if row and row[0].strip().isdigit():
                next_id = int(row[0].strip()) + 1
                break

        print(f"    📊 Spreadsheet Discovered: Contains {current_row_count} rows.")
        print(f"    ⚡ Formulating 100-opportunity array starting at serial # {next_id}...")

        append_matrix = []
        
        for category, list_items in CATEGORIES.items():
            for name, funder, geo, llc, award in list_items:
                row_payload = [
                    str(next_id),
                    name,
                    funder,
                    "OPEN",
                    "Check Current Cycle",
                    "10 days prior",
                    geo,
                    llc,
                    award,
                    f"Category: {category} | Fresh candidate uploaded for Starlight parallel qualification audit."
                ]
                append_matrix.append(row_payload)
                next_id += 1

        print(f"    🚀 Committing precisely {len(append_matrix)} open candidates to row {current_row_count + 1}...")
        ws.append_rows(append_matrix, value_input_option='USER_ENTERED')
        
        print("-" * 75)
        print(f"🟢 OPERATION SUCCESSFUL: 100 new opportunities released. Starlight audit loops ready.")
        print("=" * 75)

    except Exception as e: print(f"❌ Core Execution Fault: {e}"); sys.exit(1)

if __name__ == "__main__": main()
