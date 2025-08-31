import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.placement.iitbhu.ac.in"
LISTING_URL = f"{BASE_URL}/forum/c/notice-board/2025-26/"
MAX_PAGES = 9

import os

# Get session ID from environment variable
SESSION_ID = os.getenv('INTERNSHIP_SESSION_ID')
cookies = {"sessionid": SESSION_ID}

ROLL_PATTERN = re.compile(r"\b\d{8}\b")  # IIT BHU roll numbers are 8 digits


def fetch_page(url):
    res = requests.get(url, cookies=cookies)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")


def count_offers_in_thread(link):
    soup = fetch_page(link)

    counts = {"selected": 0, "waitlisted": 0, "under_review": 0}
    current_section = "selected"  # default until keywords appear

    for post in soup.select("td.post-content"):
        raw = post.decode_contents().replace("<br/>", "\n")
        lines = [
            line.strip()
            for line in BeautifulSoup(raw, "html.parser").get_text().split("\n")
        ]

        for line in lines:
            lower = line.lower()

            # Switch section when markers appear
            if "waitlist" in lower:
                current_section = "waitlisted"
                continue
            if "under review" in lower or "shortlist" in lower:
                current_section = "under_review"
                continue

            # Count roll numbers in current section
            if ROLL_PATTERN.search(line):
                counts[current_section] += 1

    return counts


def clean_company_name(title: str) -> str:
    title = re.sub(r"\[.*?\]", "", title)
    title = re.sub(r"^topic:\s*", "", title, flags=re.IGNORECASE)
    title = title.strip()
    return title.split()[0].capitalize() if title else "Unknown"


def scrape_offers():
    offers_by_company = {}
    totals = {"selected": 0, "waitlisted": 0, "under_review": 0}

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

            if (
                ("intern" in title_lower or "internship" in title_lower)
                and ("offer" in title_lower or "offers" in title_lower)
                and not any(
                    x in title_lower
                    for x in ["ppo", "pre-placement", "shortlist", "interview"]
                )
            ):
                print(f"🔎 Checking {title} ...")
                company_counts = count_offers_in_thread(link)

                if sum(company_counts.values()) > 0:
                    company_name = clean_company_name(title)
                    if company_name not in offers_by_company:
                        offers_by_company[company_name] = {
                            "selected": 0,
                            "waitlisted": 0,
                            "under_review": 0,
                        }

                    # Add to company and totals
                    for k in totals:
                        offers_by_company[company_name][k] += company_counts[k]
                        totals[k] += company_counts[k]

    return offers_by_company, totals


if __name__ == "__main__":
    offers_by_company, totals = scrape_offers()
    print("\n📊 Internship offers by company:")
    for company, counts in offers_by_company.items():
        print(
            f"- {company}: Selected={counts['selected']}, "
            f"Waitlisted={counts['waitlisted']}, Under Review={counts['under_review']}"
        )

    print(
        f"\n🔥 Totals: "
        f"Selected={totals['selected']}, "
        f"Waitlisted={totals['waitlisted']}, "
        f"Under Review={totals['under_review']}, "
        f"Overall={sum(totals.values())}"
    )
