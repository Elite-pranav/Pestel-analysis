import subprocess
import time
import sys

def run_script(script_name):
    """Run a Python script using the same Python interpreter running this script."""
    print(f"\n🚀 Running {script_name}...\n")
    start_time = time.time()
    
    try:
        subprocess.run([sys.executable, script_name], check=True)  # Use the current Python interpreter
        print(f"✅ {script_name} completed successfully in {time.time() - start_time:.2f} seconds\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running {script_name}: {e}")

def main():
    print("\n📌 Starting the Automated PESTEL Analysis Pipeline\n")

    # Step 1: Extract URLs
    run_script("bing_scrap_urls.py")

    # Step 2: Scrape Data from URLs
    run_script("extract_data.py")

    # Step 3: Summarize Data
    run_script("summarization.py")

    print("\n🎯 Pipeline Execution Completed! Check 'summary.json' for the final output.\n")

if __name__ == "__main__":
    main()
