import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://placement.iitbhu.ac.in"
LISTING_URL = f"{BASE_URL}/forum/c/notice-board/2025-26/"
MAX_PAGES = 9

import os

# Get session ID from environment variable
SESSION_ID = os.getenv('PPO_SESSION_ID')
cookies = {"sessionid": SESSION_ID}

ROLL_PATTERN = re.compile(r"\b\d{8}\b")  # IIT BHU roll numbers are 8 digits


def fetch_page(url):
    res = requests.get(url, cookies=cookies)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")


def count_ppos_in_thread(link):
    soup = fetch_page(link)
    selected = 0
    waitlist = 0
    under_review = 0

    for post in soup.select("td.post-content"):
        # extract lines
        raw = post.decode_contents().replace("<br/>", "\n")
        lines = [
            line.strip()
            for line in BeautifulSoup(raw, "html.parser").get_text().split("\n")
        ]

        current_section = "selected"
        for line in lines:
            lower = line.lower()

            # detect section switches
            if "waitlist" in lower:
                current_section = "waitlist"
                continue
            if "under review" in lower:
                current_section = "under_review"
                continue

            # count roll numbers in current section
            if ROLL_PATTERN.search(line):
                if current_section == "selected":
                    selected += 1
                elif current_section == "waitlist":
                    waitlist += 1
                elif current_section == "under_review":
                    under_review += 1

    return selected, waitlist, under_review


def clean_company_name(title: str) -> str:
    title = re.sub(r"\[.*?\]", "", title)  # remove [Updated]
    title = re.sub(r"^topic:\s*", "", title, flags=re.IGNORECASE)
    title = title.strip()
    return title.split()[0].capitalize() if title else "Unknown"


def scrape_ppos():
    results = {}
    totals = {"selected": 0, "waitlist": 0, "under_review": 0}

    for page in range(1, MAX_PAGES + 1):
        print(f"\n🌐 Scraping page {page} ...")
        page_url = LISTING_URL + f"?page={page}"
        soup = fetch_page(page_url)

        for row in soup.select("tr.topic-row"):
            title_tag = row.select_one("td.topic-name a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            title_lower = title.lower()
            link = BASE_URL + title_tag["href"]

            # only pick PPO threads
            if "ppo" in title_lower or "pre-placement" in title_lower:
                print(f"🔎 Checking {title} ...")
                s, w, u = count_ppos_in_thread(link)

                if s + w + u > 0:
                    company = clean_company_name(title)
                    if company not in results:
                        results[company] = {"selected": 0, "waitlist": 0, "under_review": 0}
                    results[company]["selected"] += s
                    results[company]["waitlist"] += w
                    results[company]["under_review"] += u

                    totals["selected"] += s
                    totals["waitlist"] += w
                    totals["under_review"] += u

    return results, totals


if __name__ == "__main__":
    results, totals = scrape_ppos()

    print("\n📊 PPO Results by company:")
    for company, counts in results.items():
        print(
            f"- {company}: "
            f"{counts['selected']} selected, "
            f"{counts['waitlist']} waitlisted, "
            f"{counts['under_review']} under review"
        )

    print("\n🔥 Totals:")
    print(f"✅ Selected: {totals['selected']}")
    print(f"⌛ Waitlisted: {totals['waitlist']}")
    print(f"📝 Under review: {totals['under_review']}")
    print(f"📌 Grand Total (all categories): {sum(totals.values())}")
