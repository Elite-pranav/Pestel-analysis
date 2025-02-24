import json
import re
import os
import spacy
from openai import OpenAI
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv

# Load .env file from the PESTEL folder
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

# Retrieve API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing! Check your .env file.")

# Load spaCy model with optimizations
nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger"])
nlp.max_length = 500000  # Reduce max length to avoid high memory usage

# Set up OpenAI API key
client = OpenAI(api_key=OPENAI_API_KEY)

# Load scraping input
with open("scraping_input.json", "r", encoding="utf-8") as f:
    scraping_input = json.load(f)

# Load scraped data (Limit to first 100 entries to reduce memory usage)
scraped_filename = f"{scraping_input['business_name'].lower()}_scraped_results.json"
with open(scraped_filename, "r", encoding="utf-8") as f:
    scraped_data = json.load(f)[:100]  # Keep only first 100 entries

# Construct PESTEL input dynamically
pestel_input = {
    "business_name": scraping_input.get("business_name", "Unknown"),
    "industry": scraping_input.get("industry", "General Industry"),
    "geographical_focus": scraping_input.get("geographical_focus", "Global"),
    "target_market": scraping_input.get("target_market", "General Market"),
    "competitors": scraping_input.get("competitors", []),
    "time_frame": scraping_input.get("time_frame", "Short-term"),
    "political_factors": scraping_input.get("political_factors", {})
}

# Step 1: Generate Dynamic Keywords Based on Input
def generate_dynamic_keywords(pestel_input):
    base_keywords = [
        "policy", "regulation", "government", "law", "compliance", "tax", "tariff",
        "trade", "subsidy", "political risk", "election", "sanctions", "stability",
        "legislation", "framework", "jurisdiction", "fines", "penalty", "prohibition"
    ]
    industry_keywords = [pestel_input["industry"].lower(), "market regulation", "business law"]
    geo_keywords = [pestel_input["geographical_focus"].lower(), "local government", "regional policies"]
    company_keywords = [pestel_input["business_name"].lower()]
    return list(set(base_keywords + industry_keywords + geo_keywords + company_keywords))

KEYWORDS = generate_dynamic_keywords(pestel_input)

# Step 2: Extract Relevant Text Using Keyword Filtering
def extract_relevant_text(scraped_data, keywords):
    for entry in scraped_data:
        if "paragraphs" in entry:
            for paragraph in entry["paragraphs"]:
                if any(keyword in paragraph.lower() for keyword in keywords):
                    yield paragraph  # Use generator instead of list to save memory

filtered_text = " ".join(list(extract_relevant_text(scraped_data, KEYWORDS))[:5000])  # Limit text to 5000 words

# Step 3: Extract Numerical & Statistical Data
def extract_numerical_data(text):
    patterns = [
        r"\d+%", r"\$\d+[\d,]*", r"€\d+[\d,]*", r"₹\d+[\d,]*",
        r"\d+\s?(billion|million|trillion)", r"\d+\.\d+"
    ]
    return set(match for pattern in patterns for match in re.findall(pattern, text))

numerical_values = extract_numerical_data(filtered_text)

# Step 4: Extract Named Entities (Government, Laws, Policies)
def extract_named_entities(text):
    doc = nlp(text[:10000])  # Process only the first 10,000 characters to reduce load
    return set(ent.text for ent in doc.ents if ent.label_ in ["LAW", "GPE", "ORG"])

named_entities = extract_named_entities(filtered_text)

# Step 5: Further Reduce Text Using TF-IDF Summarization
def get_top_sentences(text, num_sentences=15):
    sentences = re.split(r'(?<=[.!?])\s+', text)[:500]  # Limit number of sentences
    vectorizer = TfidfVectorizer(stop_words="english", max_features=500)  # Reduce TF-IDF vector size
    tfidf_matrix = vectorizer.fit_transform(sentences)
    sentence_scores = tfidf_matrix.sum(axis=1).flatten().tolist()
    
    ranked_sentences = sorted(
        zip(sentences, sentence_scores),
        key=lambda x: x[1],
        reverse=True
    )
    return " ".join([s[0] for s in ranked_sentences[:num_sentences]])

compressed_text = get_top_sentences(filtered_text, num_sentences=15)

# Step 6: Generate Summary with OpenAI
def generate_summary(text, numbers, entities):
    prompt = f"""
    You are an expert in business and political analysis. Keep the following business context in mind:

    **Business Name**: {pestel_input['business_name']}  
    **Industry**: {pestel_input['industry']}  
    **Geographical Focus**: {pestel_input['geographical_focus']}  
    **Target Market**: {pestel_input['target_market']}  
    **Competitors**: {", ".join(pestel_input['competitors']) if pestel_input['competitors'] else "No specific competitors mentioned"}  
    **Time Frame**: {pestel_input['time_frame']}  

#### **1. Summary (Strictly 15 Sentences)**  
- The summary must be **exactly 15 sentences**, with each sentence **on a new line**.  
- Each sentence should be **concise** and convey **one key insight** about the political factors.  
- Include numerical data: {", ".join(numbers)}  
- Mention key policies, laws, and organizations: {", ".join(entities)}

#### **2. Political Factor Analysis (Point-Wise)**  
- Analyze **only** the political factors that are set to `True`.  
- Provide **exactly 3 distinct key points** for each.  
- All insights should remain **business- and industry-relevant**.

### **Extracted Text for Analysis:**  
{text}
    """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content

enabled_factors = {key: value for key, value in pestel_input["political_factors"].items() if value}

final_summary = generate_summary(compressed_text, numerical_values, named_entities)

# Save the summary
output_filename = f"{pestel_input['business_name'].lower()}_political_summary.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump({"summary": final_summary}, f, indent=4, ensure_ascii=False)

print(f"\n✅ Summary generated and saved in '{output_filename}'")
