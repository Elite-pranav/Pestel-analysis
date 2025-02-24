import requests
import json

# Load input dynamically from scraping_input.json
with open("scraping_input.json", "r", encoding="utf-8") as f:
    user_input = json.load(f)

BING_API_KEY = os.getenv("BING_API_KEY") # Replace with your actual Bing API Key

def generate_search_queries(user_input):
    """Generate categorized Bing search queries focusing on political factors, news, government sites, and research papers."""
    business_name = user_input.get("business_name", "")
    industry = user_input.get("industry", "")
    geographical_focus = user_input.get("geographical_focus", "")
    competitors = " OR ".join(user_input.get("competitors", []))

    political_factors = user_input.get("political_factors", {})
    keywords = " ".join([key.replace("_", " ") for key, value in political_factors.items() if value])

    # News queries (7-8 URLs)
    news_queries = [
        f"{business_name} {industry} {geographical_focus} political impact {keywords}",
        f"{business_name} {industry} {geographical_focus} election effects {keywords}",
        f"{business_name} {industry} {geographical_focus} government intervention {keywords}",
        f"{business_name} {industry} {geographical_focus} policy changes {keywords}",
        f"{business_name} {industry} {geographical_focus} political controversies {keywords}",
        f"{business_name} {industry} {geographical_focus} political stability {keywords}",
        f"{business_name} {industry} {geographical_focus} legal issues {keywords}"
    ]

    # Government queries (5-6 URLs)
    government_queries = [
        f"site:.gov {business_name} {industry} {geographical_focus} policies laws",
        f"site:.gov {business_name} {industry} {geographical_focus} official regulations",
        f"site:.gov {business_name} {industry} {geographical_focus} government reports",
        f"site:.gov {business_name} {industry} {geographical_focus} legal framework",
        f"site:.gov {business_name} {industry} {geographical_focus} tax policies"
    ]

    # Research queries (2-3 URLs)
    research_queries = [
        f"site:.edu OR site:.org {business_name} {industry} {geographical_focus} academic research",
        f"site:researchgate.net OR site:sciencedirect.com {business_name} {industry} {geographical_focus} study",
        f"site:jstor.org {business_name} {industry} {geographical_focus} economic impact"
    ]

    return {"news": news_queries, "government": government_queries, "research": research_queries}

def get_relevant_urls(api_key, queries):
    """Fetch categorized results from Bing API."""
    categorized_urls = {"news": [], "government": [], "research": []}
    headers = {"Ocp-Apim-Subscription-Key": api_key}

    for category, query_list in queries.items():
        for query in query_list:
            url = f"https://api.bing.microsoft.com/v7.0/search?q={query}&count=10"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                search_results = response.json()
                urls = [item["url"] for item in search_results.get("webPages", {}).get("value", [])]
                categorized_urls[category].extend(urls)

            else:
                print(f"Error: {response.status_code}, {response.text}")

    # Remove duplicates and limit results per category
    for category in categorized_urls:
        categorized_urls[category] = list(set(categorized_urls[category]))[:8 if category == "news" else 6 if category == "government" else 3]

    return categorized_urls

# Fetch categorized URLs
queries = generate_search_queries(user_input)
categorized_urls = get_relevant_urls(BING_API_KEY, queries)

# Save results
output_filename = f"{user_input['business_name'].lower()}_scraped_urls.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(categorized_urls, f, indent=4, ensure_ascii=False)

# Output results
print("\n✅ Scraped Website URLs:")
for category, urls in categorized_urls.items():
    print(f"\n📌 {category.capitalize()} URLs:")
    for url in urls:
        print(url)

print(f"\n✅ URLs saved to '{output_filename}'")
