"""
========================================================
 Bookstore Web Scraping Pipeline
 Target  : https://books.toscrape.com
 Author  : Oluwasegun Raphael
 Tools   : Python, Requests, BeautifulSoup, Pandas
========================================================

Business Context:
    A retail analytics team needs structured data on book inventory,
    pricing, ratings, and availability across all categories from an
    online bookstore. This pipeline automates end-to-end extraction,
    validation, and delivery of a clean, analysis-ready dataset.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import os
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────────────────────

BASE_URL   = "https://books.toscrape.com"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
LOG_DIR    = os.path.join(os.path.dirname(__file__), "..", "outputs")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}

# ─── Logging Setup ────────────────────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "scraper.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_soup(url: str) -> BeautifulSoup | None:
    """Fetch a page and return a BeautifulSoup object. Returns None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def get_all_categories(soup: BeautifulSoup) -> dict[str, str]:
    """Extract all category names and their URLs from the sidebar."""
    categories = {}
    nav = soup.select("ul.nav-list > li > ul > li > a")
    for tag in nav:
        name = tag.text.strip()
        url  = BASE_URL + "/" + tag["href"]
        categories[name] = url
    logger.info(f"Found {len(categories)} categories.")
    return categories


def parse_book(article, category: str) -> dict:
    """Parse a single book article element into a structured dictionary."""
    title  = article.h3.a["title"]
    price  = article.select_one("p.price_color").text.strip().replace("Â", "").replace("£", "").strip()
    rating_word = article.p["class"][1]
    rating = RATING_MAP.get(rating_word, 0)
    avail  = article.select_one("p.availability").text.strip()
    rel_url = article.h3.a["href"].replace("../", "")

    return {
        "title"       : title,
        "category"    : category,
        "price_gbp"   : float(price),
        "rating"      : rating,
        "availability": avail,
        "url"         : f"{BASE_URL}/catalogue/{rel_url}"
    }


def scrape_category(category_name: str, category_url: str) -> list[dict]:
    """Scrape all pages of a single category and return a list of book records."""
    books   = []
    page_url = category_url

    while page_url:
        soup = get_soup(page_url)
        if not soup:
            break

        articles = soup.select("article.product_pod")
        for article in articles:
            books.append(parse_book(article, category_name))

        # Pagination — check for a "next" button
        next_btn = soup.select_one("li.next > a")
        if next_btn:
            base = category_url.rsplit("/", 1)[0]
            page_url = base + "/" + next_btn["href"]
            time.sleep(0.5)   # polite delay between pages
        else:
            page_url = None

    logger.info(f"  [{category_name}] scraped {len(books)} books.")
    return books


# ─── Data Validation ──────────────────────────────────────────────────────────

def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Run quality checks and flag anomalies."""
    logger.info("Running data validation...")

    initial = len(df)

    # Drop exact duplicates
    df = df.drop_duplicates(subset=["title", "category"])
    logger.info(f"  Duplicates removed : {initial - len(df)}")

    # Flag missing values
    missing = df.isnull().sum()
    if missing.any():
        logger.warning(f"  Missing values:\n{missing[missing > 0]}")

    # Flag price anomalies
    anomalies = df[df["price_gbp"] <= 0]
    if not anomalies.empty:
        logger.warning(f"  {len(anomalies)} records with invalid price (<=0)")

    # Add data quality flag
    df["data_quality"] = "OK"
    df.loc[df["price_gbp"] <= 0,       "data_quality"] = "INVALID_PRICE"
    df.loc[df["title"].isnull(),        "data_quality"] = "MISSING_TITLE"
    df.loc[df["availability"] == "",    "data_quality"] = "MISSING_AVAILABILITY"

    logger.info(f"  Final record count : {len(df)}")
    return df


# ─── Export ───────────────────────────────────────────────────────────────────

def export(df: pd.DataFrame):
    """Export cleaned dataset to CSV and JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path  = os.path.join(OUTPUT_DIR, f"books_{timestamp}.csv")
    json_path = os.path.join(OUTPUT_DIR, f"books_{timestamp}.json")

    df.to_csv(csv_path,  index=False)
    df.to_json(json_path, orient="records", indent=2)

    logger.info(f"CSV  saved → {csv_path}")
    logger.info(f"JSON saved → {json_path}")

    return csv_path, json_path


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def run_pipeline(max_categories: int = None):
    """
    Full end-to-end scraping pipeline.
    
    Args:
        max_categories: Limit categories scraped (None = all 50).
                        Set to 3-5 for a quick test run.
    """
    logger.info("=" * 55)
    logger.info(" Bookstore Scraping Pipeline — Starting")
    logger.info("=" * 55)

    # Step 1: Get homepage and extract categories
    soup = get_soup(BASE_URL)
    if not soup:
        logger.error("Could not reach the website. Check your connection.")
        return

    categories = get_all_categories(soup)

    if max_categories:
        categories = dict(list(categories.items())[:max_categories])
        logger.info(f"Running in test mode — scraping {max_categories} categories.")

    # Step 2: Scrape each category
    all_books = []
    for i, (name, url) in enumerate(categories.items(), 1):
        logger.info(f"Scraping category {i}/{len(categories)}: {name}")
        all_books.extend(scrape_category(name, url))
        time.sleep(0.8)   # polite delay between categories

    # Step 3: Build DataFrame
    df = pd.DataFrame(all_books)
    logger.info(f"\nRaw records collected: {len(df)}")

    # Step 4: Validate
    df = validate(df)

    # Step 5: Export
    csv_path, json_path = export(df)

    logger.info("=" * 55)
    logger.info(" Pipeline Complete")
    logger.info(f" Total books scraped : {len(df)}")
    logger.info(f" Categories covered  : {df['category'].nunique()}")
    logger.info(f" Avg price (£)       : {df['price_gbp'].mean():.2f}")
    logger.info(f" Avg rating          : {df['rating'].mean():.2f}")
    logger.info("=" * 55)

    return df


if __name__ == "__main__":
    # Change max_categories=None to scrape all 50 categories (~1000 books)
    # Use max_categories=3 for a quick test
    df = run_pipeline(max_categories=None)
