from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import time
import sys
import json
import os


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route('/')
def home():
    return "Flask is running!"


@app.route('/get_summary/<business_name>', methods=['GET'])
def get_summary(business_name):
    summary_file = f"{business_name.lower()}_political_summary.json"
    
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8") as file:
            summary_data = json.load(file)
        return jsonify(summary_data)
    
    return jsonify({"error": "Summary not found"}), 404


def run_script(script_name):
    """Runs a Python script with the correct path."""
    script_path = os.path.join(os.getcwd(), "backend", script_name)  # Full path
    print(f"\n🚀 Running {script_path}...\n")
    
    start_time = time.time()
    try:
        subprocess.run([sys.executable, script_path], check=True)  # Execute script
        print(f"✅ {script_name} completed successfully in {time.time() - start_time:.2f} seconds\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running {script_name}: {e}")
        return False


@app.route("/analyze_pestel", methods=["POST"])
def analyze_pestel():
    """API endpoint to trigger PESTEL analysis."""
    data = request.json  # Get data from frontend
    print("\n📌 Received Data:", data)

    # Convert political_factors list to a dictionary
    data["political_factors"] = {factor: True for factor in data["political_factors"]}

    # Save input to scraping_input.json
    with open("scraping_input.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print("✅ Input saved to scraping_input.json")

    # Step 1: Extract URLs
    if not run_script("backend/bing_scrap_urls.py"):
        return jsonify({"error": "Failed at URL extraction"}), 500

    # Step 2: Scrape Data
    if not run_script("backend/extract_data.py"):
        return jsonify({"error": "Failed at Data Extraction"}), 500

    # Step 3: Summarize Data
    if not run_script("backend/summarization.py"):
        return jsonify({"error": "Failed at Summarization"}), 500

    summary_file = f"{data['business_name'].lower()}_political_summary.json"

    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = json.load(f)  # Use json.load instead of f.read()
    except Exception as e:
        return jsonify({"error": f"Failed to read summary: {e}"}), 500

    return jsonify({"message": "PESTEL analysis completed successfully!", "results": summary}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
