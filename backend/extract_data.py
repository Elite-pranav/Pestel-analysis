import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# Set up ScraperAPI key
SCRAPER_API_KEY =  os.getenv("SCRAPER_API_KEY")

# Headers to simulate a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_page(url):
    """Try normal requests first, fallback to ScraperAPI if blocked."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.text
        print(f"🔴 {url} blocked (Status {response.status_code}), using ScraperAPI...")
    except requests.RequestException as e:
        print(f"⚠️ Error fetching {url}: {e}")
    
    # Fallback to ScraperAPI
    scraper_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={url}"
    try:
        response = requests.get(scraper_url, timeout=15)
        if response.status_code == 200:
            return response.text
        print(f"❌ ScraperAPI also failed for {url} (Status {response.status_code})")
    except requests.RequestException as e:
        print(f"⚠️ ScraperAPI request failed for {url}: {e}")
    return None

def extract_text_and_tables(html_content):
    """Extract title, text, and structured tables from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
        tag.extract()

    # Get title safely
    title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"

    # Extract paragraphs
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    
    # Extract tables with structure
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            rows.append(cells)
        if rows:
            tables.append(rows)

    # Convert tables into readable dictionaries
    structured_tables = []
    for table in tables:
        if len(table) > 1:
            headers = table[0]  # First row as headers
            data = table[1:]  # Remaining rows as data
            structured_tables.append([dict(zip(headers, row)) for row in data if len(row) == len(headers)])

    return {
        "title": title,
        "paragraphs": paragraphs,
        "word_count": sum(len(p.split()) for p in paragraphs),
        "tables": structured_tables
    }


def scrape_urls(url_list):
    """Scrape multiple URLs and return structured data."""
    results = []
    
    for url in url_list:
        print(f"🟢 Scraping: {url}")
        html_content = fetch_page(url)
        
        if html_content:
            extracted_data = extract_text_and_tables(html_content)
            extracted_data["url"] = url
            results.append(extracted_data)
        else:
            results.append({
                "url": url,
                "error": "Failed to retrieve content"
            })
    
    return results
# Load user input from JSON
with open("scraping_input.json", "r", encoding="utf-8") as f:
    user_input = json.load(f)
    
    
# Get business name dynamically
business_name = user_input['business_name'].lower()

# Define dynamic file names
input_filename = f"{business_name}_scraped_urls.json"
output_filename = f"{business_name}_scraped_results.json"


# Load scraped URLs from JSON
with open(input_filename, "r", encoding="utf-8") as f:
    data = json.load(f)
urls_to_scrape = data.get("news", []) + data.get("government", []) + data.get("research", [])

# Scrape all URLs and save results
scraped_data = scrape_urls(urls_to_scrape)

# Save results to JSON file (structured)
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(scraped_data, f, indent=4, ensure_ascii=False)

print(f"\n✅ Scraping completed. Data saved in {output_filename}")
