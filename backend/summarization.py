import json
import re
from openai import OpenAI
import spacy
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Load spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 5000000  # Set a higher limit (5 million characters)


# Set up OpenAI API key
OPENAI_API_KEY =  os.getenv("OPENAI_API_KEY")   # Replace with your actual API key
client = OpenAI(api_key=OPENAI_API_KEY)

# Load scraping input
with open("scraping_input.json", "r", encoding="utf-8") as f:
    scraping_input = json.load(f)

# Load scraped data
scraped_filename = f"{scraping_input['business_name'].lower()}_scraped_results.json"
with open(scraped_filename, "r", encoding="utf-8") as f:
    scraped_data = json.load(f)

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
    
    # Add keywords dynamically based on industry, geography, and business name
    industry_keywords = [pestel_input["industry"].lower(), "market regulation", "business law"]
    geo_keywords = [pestel_input["geographical_focus"].lower(), "local government", "regional policies"]
    company_keywords = [pestel_input["business_name"].lower()]
    
    return list(set(base_keywords + industry_keywords + geo_keywords + company_keywords))

KEYWORDS = generate_dynamic_keywords(pestel_input)

# Step 2: Extract Relevant Text Using Keyword Filtering
def extract_relevant_text(scraped_data, keywords):
    relevant_text = []
    
    for entry in scraped_data:
        if "paragraphs" in entry:
            for paragraph in entry["paragraphs"]:
                if any(keyword in paragraph.lower() for keyword in keywords):
                    relevant_text.append(paragraph)
    
    return " ".join(relevant_text)

filtered_text = extract_relevant_text(scraped_data, KEYWORDS)

# Step 3: Extract Numerical & Statistical Data
def extract_numerical_data(text):
    # Extract percentages, monetary values, and numerical data
    patterns = [
        r"\d+%",               # Percentage values (e.g., 25%)
        r"\$\d+[\d,]*",        # Dollar amounts (e.g., $5,000)
        r"€\d+[\d,]*",         # Euro amounts (e.g., €1,200)
        r"₹\d+[\d,]*",         # Indian Rupees (e.g., ₹10,000)
        r"\d+\s?(billion|million|trillion)",  # Large values (e.g., 5 billion)
        r"\d+\.\d+",           # Decimal values (e.g., 3.5%)
    ]
    
    numerical_data = []
    for pattern in patterns:
        numerical_data += re.findall(pattern, text)
    
    return set(numerical_data)  # Remove duplicates

numerical_values = extract_numerical_data(filtered_text)

# Step 4: Extract Named Entities (Government, Laws, Policies)
def extract_named_entities(text):
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["LAW", "GPE", "ORG"]]
    return set(entities)

named_entities = extract_named_entities(filtered_text)

# Step 5: Further Reduce Text Using TF-IDF Summarization
def get_top_sentences(text, num_sentences=15):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split into sentences
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(sentences)
    sentence_scores = tfidf_matrix.sum(axis=1).flatten().tolist()
    
    ranked_sentences = [
        (sentence, score) for sentence, score in zip(sentences, sentence_scores)
    ]
    ranked_sentences = sorted(ranked_sentences, key=lambda x: x[1], reverse=True)
    
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
    
    
    ### **Task:**  
Generate a **political analysis** based on the extracted text.  
 
#### **1. Summary (Strictly 15 Sentences)**  
- The summary must be **exactly 20 sentences**, with each sentence **on a new line**.  
- Each sentence should be **concise** (no more than 60 words) and convey **one key insight** about the political factors you have recieved.  
- Maintain a balance between **statistical data** (e.g., tax rates, regulations) and **textual analysis** (e.g., implications, trends).  
- Avoid redundancy—each sentence should introduce a new aspect of the analysis.  
- Include numerical data: {", ".join(numbers)}  
- Mention key policies, laws, and organizations: {", ".join(entities)}

#### **2. Political Factor Analysis (Point-Wise)**  
- Analyze **only** the political factors that are set to `True`.  
- For **each enabled political factor**, provide **exactly 3 distinct key points**.  
- Each point must be **directly relevant** to {pestel_input['business_name']} and the {pestel_input['industry']} industry.  
- **Use real-world data or insights** where applicable—avoid vague or overly generic statements.  

**Enabled Political Factors:**  
{", ".join(enabled_factors.keys()) if enabled_factors else "None"}  

### **Important Constraints:**  
- Keep the language **formal and analytical**.  
- Ensure **strict adherence** to sentence and point limits.  
- All insights should remain **business- and industry-relevant**.  
  

Here is the extracted text for analysis:

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
