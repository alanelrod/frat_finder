import os
import time
import csv
import pandas as pd
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process

# === CONFIG ===
FRAT = "ATO"  # ← Change to SAE, PIKE, etc.
CHAPTER_CSV = f"/Users/alanelrod/Desktop/frat_finder/fratDBs/{FRAT}.csv"
UNIV_CSV = "/Users/alanelrod/Desktop/frat_finder/filtered_universities.csv"
OUTPUT_FOLDER = f"frat_results_per_school/{FRAT}"
RESULTS_PER_SCHOOL = 3
SLEEP_SECONDS = 1.5
DUCK_URL = "https://html.duckduckgo.com/html/"

# === TOR PROXY + HEADERS ===
PROXIES = {
    "http": "socks5h://localhost:9050",
    "https": "socks5h://localhost:9050"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# === SETUP ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === LOAD DATA ===
chapter_df = pd.read_csv(CHAPTER_CSV)
school_df = pd.read_csv(UNIV_CSV)

chapter_insts = chapter_df["Institution"].dropna().tolist()
school_insts = school_df["Institution Name"].dropna().tolist()

# === STEP 1: EXACT MATCH ===
exact_matches = []
fuzzy_candidates = []

for chapter_school in chapter_insts:
    if chapter_school in school_insts:
        exact_matches.append(chapter_school)
    else:
        fuzzy_candidates.append(chapter_school)

# === STEP 2: FUZZY MATCH ===
fuzzy_matches = []
for chapter in fuzzy_candidates:
    match = process.extractOne(chapter, school_insts, scorer=fuzz.token_set_ratio)
    if match and match[1] >= 80:
        fuzzy_matches.append(match[0])

# === STEP 3: COMBINE MATCHES ===
matched_schools = list(set(exact_matches + fuzzy_matches))
print(f"✅ Exact matches: {len(exact_matches)}")
print(f"🔎 Fuzzy matches added: {len(fuzzy_matches)}")
print(f"🎯 Total matched schools for {FRAT}: {len(matched_schools)}")

# === STEP 4: SCRAPE LINKS ===
for school in matched_schools:
    csv_filename = os.path.join(OUTPUT_FOLDER, f"{school.replace('/', '_')[:50]}.csv")
    if os.path.exists(csv_filename):
        print(f"🟡 Skipping {school} (already exists)")
        continue

    query = f"{school} {FRAT} frat"
    print(f"🔍 Searching: {query}")

    try:
        response = requests.post(DUCK_URL, data={"q": query}, headers=HEADERS, proxies=PROXIES, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.text.lower()
            if any(key in text for key in [FRAT.lower(), "frat"]):
                if href.startswith("http"):
                    links.append(href)
            if len(links) >= RESULTS_PER_SCHOOL:
                break

        while len(links) < RESULTS_PER_SCHOOL:
            links.append("")

        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Institution", "Query", "Link 1", "Link 2", "Link 3"])
            writer.writerow([school, query] + links)

        print(f"✅ Saved: {csv_filename}")

    except Exception as e:
        print(f"❌ Error for {school}: {e}")
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Institution", "Query", "Link 1", "Link 2", "Link 3"])
            writer.writerow([school, query, "ERROR", "", ""])

    time.sleep(SLEEP_SECONDS)
