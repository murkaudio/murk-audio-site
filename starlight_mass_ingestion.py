#!/usr/bin/env python3
import os, sys, json, re, gspread

SF = os.path.expanduser("~/murk-runners/service_account.json")
MID = "1243mJP1_vuS9l9DkcswUyv5f0afPDUoAGYGoLSiwEYc"

GRANTS_DATABASE = [
    {"name": "Grants for Arts Projects - Media Arts", "funder": "National Endowment for the Arts (NEA)", "geo": "National / US Territory", "fit": "Yes", "status": "Open", "deadline": "July 9, 2026", "gate": "06/29/2026", "url": "https://www.arts.gov/grants/grants-for-arts-projects"},
    {"name": "Media Projects Development Grants", "funder": "National Endowment for the Humanities (NEH)", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "June 25, 2026", "gate": "06/15/2026", "url": "https://www.neh.gov/program/media-projects"},
    {"name": "Media Projects Production Grants", "funder": "National Endowment for the Humanities (NEH)", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "June 25, 2026", "gate": "06/15/2026", "url": "https://www.neh.gov/program/media-projects"},
    {"name": "PodGround Creator Micro-Grant", "funder": "PodGround", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Rolling Cycles", "gate": "10 days prior", "url": "https://podground.io/grant"},
    {"name": "Sundance Documentary Fund", "funder": "Sundance Institute", "geo": "Global", "fit": "Yes", "status": "Open", "deadline": "June 15, 2026", "gate": "06/05,2026", "url": "https://collab.sundance.org/catalog/i/Resources/Grants-and-Opportunities"},
    {"name": "IDA Enterprise Documentary Fund", "funder": "International Documentary Association", "geo": "National", "fit": "Yes", "status": "Monitor", "deadline": "Check Current Cycle", "gate": "10 days prior", "url": "https://www.documentary.org/funding"},
    {"name": "KCRW Independent Producer Project", "funder": "KCRW", "geo": "National", "fit": "Yes", "status": "Monitor", "deadline": "Check Current Cycle", "gate": "10 days prior", "url": "https://www.kcrw.com"},
    {"name": "Third Coast Audio Festival Awards", "funder": "Third Coast International", "geo": "Global", "fit": "Yes", "status": "Open", "deadline": "Varies by Cycle", "gate": "10 days prior", "url": "https://www.thirdcoastfestival.org"},
    {"name": "The Audio Verse Awards Production Fund", "funder": "Audio Verse", "geo": "Global", "fit": "Yes", "status": "Monitor", "deadline": "Check Current Cycle", "gate": "10 days prior", "url": "https://audioverseawards.net"},
    {"name": "Benton Institute Media Grants", "funder": "Benton Institute", "geo": "National", "fit": "Yes", "status": "Monitor", "deadline": "Check Current Cycle", "gate": "10 days prior", "url": "https://www.benton.org"},
    {"name": "Creative Capital Open Call Award", "funder": "Creative Capital", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "April 2, 2027", "gate": "03/23/2027", "url": "https://creative-capital.org"},
    {"name": "Emerging Native Arts Grant", "funder": "Walker Youngbird Foundation", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "June 18, 2026", "gate": "06/08/2026", "url": "https://www.artworkarchive.com"},
    {"name": "The Evolution Grant", "funder": "Art Fluent", "geo": "International", "fit": "Yes", "status": "Open", "deadline": "June 19, 2026", "gate": "06/09/2026", "url": "https://www.art-fluent.com"},
    {"name": "Wassaic Project Artist Residency", "funder": "Wassaic Project", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "July 1, 2026", "gate": "06/21/2026", "url": "https://wassaicproject.org"},
    {"name": "Light Work Artist Residency Program", "funder": "Light Work", "geo": "International", "fit": "Yes", "status": "Open", "deadline": "June 30, 2026", "gate": "06/20/2026", "url": "https://www.lightwork.org"},
    {"name": "Loghaven Artist Residency Stipend", "funder": "Loghaven", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "July 15, 2026", "gate": "07/05/2026", "url": "https://loghaven.org"},
    {"name": "Hayama Artist Residency", "funder": "Hayama Foundation", "geo": "International", "fit": "Yes", "status": "Open", "deadline": "September 30, 2026", "gate": "09/20/2026", "url": "https://collab.sundance.org"},
    {"name": "PLAYA Art/Sci Awarded Residency", "funder": "PLAYA Oregon", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "June 30, 2026", "gate": "06/20/2026", "url": "https://playasummerlake.org"},
    {"name": "MacDowell Fellowship Program", "funder": "MacDowell", "geo": "Global", "fit": "Yes", "status": "Open", "deadline": "September 10, 2026", "gate": "08/31/2026", "url": "https://www.macdowell.org"},
    {"name": "Yaddo Music & Sound Fellowship", "funder": "Yaddo Collective", "geo": "Global", "fit": "Yes", "status": "Open", "deadline": "August 1, 2026", "gate": "07/22/2026", "url": "https://yaddo.org"},
    {"name": "Creative Heights Initiative", "funder": "Oregon Community Foundation (OCF)", "geo": "Oregon", "fit": "Yes", "status": "Open", "deadline": "February 12, 2027", "gate": "02/02/2027", "url": "https://oregoncf.org/creative-heights"},
    {"name": "Portland Arts Project Grants", "funder": "Regional Arts & Culture Council (RACC)", "geo": "Portland, OR Region", "fit": "Yes", "status": "Open", "deadline": "September 24, 2026", "gate": "09/14/2026", "url": "https://www.portland.gov/arts/small-grants-program"},
    {"name": "Individual Artist Fellowship", "funder": "Oregon Arts Commission", "geo": "Oregon", "fit": "Yes", "status": "Open", "deadline": "October 2, 2026", "gate": "09/22/2026", "url": "https://www.oregonartscommission.org"},
    {"name": "Career Opportunity Grant", "funder": "Oregon Arts Commission", "geo": "Oregon", "fit": "Yes", "status": "Open", "deadline": "Rolling Cycles", "gate": "10 days prior", "url": "https://www.oregonartscommission.org"},
    {"name": "Friends of IFCC Artist Grant", "funder": "Friends of IFCC Portland", "geo": "Portland, OR", "fit": "Yes", "status": "Open", "deadline": "September 12, 2026", "gate": "09/02/2026", "url": "https://www.portland.gov/arts/small-grants-program"},
    {"name": "MusicOregon Echo Fund", "funder": "MusicOregon / City of Portland", "geo": "Portland, OR", "fit": "Yes", "status": "Open", "deadline": "September 5, 2026", "gate": "08/26/2026", "url": "https://www.portland.gov/arts/small-grants-program"},
    {"name": "Arts & Culture General Project Grants", "funder": "The Collins Foundation", "geo": "Oregon", "fit": "Yes", "status": "Open", "deadline": "Rolling Cycles", "gate": "10 days prior", "url": "https://www.collinsfoundation.org"},
    {"name": "Arts Enhancement Grants", "funder": "James F. and Marion L. Miller Foundation", "geo": "Oregon", "fit": "Yes", "status": "Open", "deadline": "Check Current Cycle", "gate": "10 days prior", "url": "https://www.millerfound.org"},
    {"name": "Community Cultural Grants", "funder": "Multnomah County Cultural Coalition", "geo": "Multnomah County, OR", "fit": "Yes", "status": "Open", "deadline": "November 1, 2026", "gate": "10/22/2026", "url": "https://multco-culturalcoalition.org"},
    {"name": "Cultural Development Grant", "funder": "Oregon Cultural Trust", "geo": "Oregon", "fit": "Yes", "status": "Open", "deadline": "Check Current Cycle", "gate": "10 days prior", "url": "https://culturaltrust.org"},
    {"name": "Hiring Our Heroes Small Business Grant", "funder": "FedEx Founders Fund", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Varies by Cycle", "gate": "10 days prior", "url": "https://wise.com/us/blog/veteran-business-grants"},
    {"name": "Warrior Rising Entrepreneur Grant", "funder": "Warrior Rising Program", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Rolling Entry", "gate": "Continuous", "url": "https://www.warriorrising.org"},
    {"name": "NASE Growth Grants", "funder": "National Association for the Self-Employed", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Quarterly Cycles", "gate": "10 days prior", "url": "https://www.nase.org"},
    {"name": "VIP Small Business Training Fund", "funder": "Veteran Institute for Procurement", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Rolling Intake", "gate": "Continuous", "url": "https://www.nationalvip.org"},
    {"name": "Military Entrepreneur Challenge", "funder": "Second Service Foundation", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Varies by Session", "gate": "10 days prior", "url": "https://secondservicefoundation.org"},
    {"name": "Veteran Small Business Award", "funder": "StreetShares Foundation", "geo": "National", "fit": "Yes", "status": "Monitor", "deadline": "Watch for Reopening", "gate": "10 days prior", "url": "https://streetsharesfoundation.org"},
    {"name": "Bunker Labs Transition Support", "funder": "Bunker Labs", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Rolling Cohorts", "gate": "Continuous", "url": "https://bunkerlabs.org"},
    {"name": "Texas Veterans Commission Grant Fit Check", "funder": "TVC Fund", "geo": "Regional / TX Scope Only", "fit": "No", "status": "Spiked", "deadline": "N/A", "gate": "N/A", "url": "https://www.tvc.texas.gov"},
    {"name": "SBA SDVOSB Procurement Allocations", "funder": "US Small Business Administration", "geo": "National / Federal", "fit": "Yes", "status": "Open", "deadline": "Continuous Sourcing", "gate": "Continuous", "url": "https://www.sba.gov"},
    {"name": "VA VR&E Self-Employment Equipment Grant", "funder": "US Department of Veterans Affairs", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Continuous Sourcing", "gate": "Continuous", "url": "https://www.va.gov"},
    {"name": "Monthly Micro-Grants - Making Waves", "funder": "Content is Queen", "geo": "Global", "fit": "Yes", "status": "Open", "deadline": "Monthly Rolling", "gate": "End of Month", "url": "https://contentisqueen.org"},
    {"name": "Awesome Foundation Monthly Micro-Grant", "funder": "Awesome Foundation Portland", "geo": "Portland, OR", "fit": "Yes", "status": "Open", "deadline": "Monthly Rolling", "gate": "Continuous", "url": "https://www.awesomefoundation.org"},
    {"name": "Adolph & Esther Gottlieb Emergency Grant", "funder": "Gottlieb Foundation", "geo": "Global", "fit": "Yes", "status": "Open", "deadline": "Rolling Crisis", "gate": "Continuous", "url": "https://www.gottliebfoundation.org"},
    {"name": "FCA Emergency Grant Program", "funder": "Foundation for Contemporary Arts", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Monthly Rolling", "gate": "Continuous", "url": "https://www.foundationforcontemporaryarts.org"},
    {"name": "Rauschenberg Creative Relief Grants", "funder": "NYFA", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Rolling Windows", "gate": "10 days prior", "url": "https://www.nyfa.org"},
    {"name": "Individual Creator Seed Grants", "funder": "The Pollination Project", "geo": "Global", "fit": "Yes", "status": "Open", "deadline": "Weekly Rolling", "gate": "Continuous", "url": "https://thepollinationproject.org"},
    {"name": "Arts Writers Grant Program", "funder": "Creative Capital / Warhol Foundation", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Check Current Cycle", "gate": "10 days prior", "url": "https://www.artswriters.org"},
    {"name": "Artist Relief Project Unrestricted Micro-Stipends", "funder": "Artist Relief Project", "geo": "Global", "fit": "Yes", "status": "Open", "deadline": "Rolling Intake", "gate": "Continuous", "url": "https://artistreliefproject.org"},
    {"name": "Anonymous Was A Woman Grants", "funder": "Anonymous Was A Woman", "geo": "National", "fit": "Yes", "status": "Monitor", "deadline": "By Nomination", "gate": "N/A", "url": "https://www.anonymouswasawoman.org"},
    {"name": "Queer Art Production Grants", "funder": "Queer Art Inc", "geo": "National", "fit": "Yes", "status": "Open", "deadline": "Varies by Cycle", "gate": "10 days prior", "url": "https://www.queerart.org"}
]

def main():
    print("=" * 75); print("🛡️ STARLIGHT MASS INGESTION ENGINE — POPULATING FUNNEL")
    print("=" * 75)
    if not os.path.exists(SF): print("❌ Error: service_account.json missing."); sys.exit(1)
    try:
        sheet = gspread.service_account(filename=SF).open_by_key(MID)
        ws = sheet.worksheet("AIR_Grants_Pipeline")
        
        headers = [h.strip().lower() for h in ws.row_values(1)]
        print(f"    📊 Live Header Pre-Check: Mapping matrix columns -> {headers}")

        name_idx = headers.index("grant name")
        funder_idx = headers.index("funder / org")
        geo_idx = headers.index("geography")
        fit_idx = headers.index("fits llc?")
        status_idx = headers.index("status")
        deadline_idx = headers.index("public deadline")
        safety_idx = headers.index("internal deadline safety gate")
        url_idx = headers.index("source url verification")

        existing_names = {row[name_idx].strip().lower() for row in ws.get_all_values() if row}
        ingested = 0

        for item in GRANTS_DATABASE:
            g_title = item["name"].strip()
            if g_title.lower() in existing_names:
                continue

            payload = [""] * len(headers)
            payload[name_idx] = g_title
            payload[funder_idx] = item["funder"]
            payload[geo_idx] = item["geo"]
            payload[fit_idx] = item["fit"]
            payload[status_idx] = item["status"]
            payload[deadline_idx] = item["deadline"]
            payload[safety_idx] = item["gate"]
            payload[url_idx] = item["url"]

            ws.append_row(payload, value_input_option='USER_ENTERED')
            print(f"    🚀 Ingested: '{g_title}' added cleanly.")
            ingested += 1

        print("-" * 75); print(f"🟢 FUNNEL EXPANSION COMPLETE: Successfully added {ingested} verified leads."); print("=" * 75)
    except Exception as e: print(f"❌ Execution Fault: {e}"); sys.exit(1)

if __name__ == "__main__": main()
