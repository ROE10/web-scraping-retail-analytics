# 📚 Bookstore Web Scraping & Analytics Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue) ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Scraping-green) ![Pandas](https://img.shields.io/badge/Pandas-Analysis-yellow) ![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## 📌 Project Overview

A retail analytics team needs structured, up-to-date data on book inventory, pricing, ratings, and availability across all categories from an online bookstore. This project automates the full end-to-end extraction, validation, and delivery of a clean, analysis-ready dataset — replacing manual data collection entirely.

The pipeline combines **Python web scraping** for automated data extraction with **Pandas** for cleaning and validation, and delivers structured outputs in both CSV and JSON formats ready for downstream analysis or BI tools.

---

## 🛠️ Tech Stack

- **Python 3.12**
  - `requests` — HTTP requests and page fetching
  - `BeautifulSoup4` — HTML parsing and data extraction
  - `lxml` — Fast HTML parser
  - `pandas` — Data cleaning, validation, and export
  - `matplotlib` / `seaborn` — Exploratory visualizations
- **Jupyter Notebook** — EDA and insight documentation
- **Git & GitHub** — Version control

---

## 📂 Repository Structure

```
bookstore_scraper/
│
├── scripts/
│   └── scraper.py                      # Main scraping pipeline
│
├── notebooks/
│   ├── analysis.ipynb                  # EDA and business insights
│   └── scraper_step_by_step.ipynb      # Walks through the entire scraping pipeline cell by cell
│
├── outputs/
│   ├── books_20260618_122007.csv       # Cleaned dataset (CSV)
│   ├── books_20260618_122007.json      # Cleaned dataset (JSON)
│   ├── scraper.log                     # Pipeline run logs
│   ├── avalaibility.png                
│   ├── price-distribution.png          
│   ├── price-vs-rating.png            
│   ├── rating_distribution.png         
│   └── top_categories_price.png   
│
└── README.md
```
---

## 📖 For Collaborators & Learners
I've also attachted the notebooks/scraper_step_by_step.ipynb walks through of the entire scraping pipeline cell by cell with detailed comments, from fetching a single page to exporting a clean dataset. Run it step by step to understand exactly how each part works before using the production script.

---

## 🔄 Pipeline Stages

```
1. Homepage fetch         → Extract all 50 category URLs
2. Category pagination    → Navigate multi-page category listings
3. Book-level extraction  → Title, price, rating, availability, URL
4. Data validation        → Deduplication, anomaly flagging, quality checks
5. Export                 → CSV + JSON with timestamp
6. EDA                    → Pricing, ratings, category analysis
```
---
## ▶️ How to Run

### 1. Install dependencies
```bash
pip install requests beautifulsoup4 pandas lxml matplotlib seaborn
```

### 2. Run the scraper
```bash
cd scripts
python scraper.py
```

> **Tip:** For a quick test run, open `scraper.py` and set `max_categories=3` in the last line. Set to `None` to scrape all 50 categories (~1000 books).

### 3. View the analysis
Open `notebooks/analysis.ipynb` in Jupyter and run all cells.

---

## 📊 Dataset Schema

| Column | Type | Description |
|---|---|---|
| `title` | string | Full book title |
| `category` | string | Book category/genre |
| `price_gbp` | float | Price in British Pounds |
| `rating` | int | Star rating (1–5) |
| `availability` | string | In stock / Out of stock |
| `url` | string | Direct link to book page |
| `data_quality` | string | Quality flag (OK / INVALID_PRICE etc.) |

---

## 📈 Key Insights

- Scraped **1000+ books** across **50 categories** with 100% field coverage
- Price distribution is right-skewed — majority of books priced under £30
- No strong correlation between price and star rating (Pearson r ≈ 0.0)
- High-price category outliers identified for promotional targeting
- Availability gaps surfaced across select categories — restocking opportunities flagged

---

## 👤 Author

**Oluwasegun Raphael**
 **Data Scientist & Analyst**
- 📧 ralpholuwashegun@gmail.com
- 🔗 [LinkedIn](http://linkedin.com/in/roe10)
- 💻 [GitHub](https://github.com/roe10)
- 🌐 [Portfolio](https://roe10.github.io)
