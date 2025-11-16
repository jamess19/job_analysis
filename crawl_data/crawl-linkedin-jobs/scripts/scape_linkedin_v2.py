import csv
import json
import os
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["linkedin", "google"], # "glassdoor", "bayt", "naukri", "bdjobs"
    search_term="software engineer",
    google_search_term="software engineer jobs near San Francisco, CA since yesterday",
    location="Vietnam",
    results_wanted=20,
    hours_old=72,
    country_indeed='USA',

    linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
print(f"Found {len(jobs)} jobs")
print(jobs.head())

# Create data-files directory path
data_dir = os.path.join(os.path.dirname(__file__), "..", "data-files")
os.makedirs(data_dir, exist_ok=True)

# Export to CSV
jobs.to_csv(os.path.join(data_dir, "linkedin_jobs.csv"), quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

# Export to JSON
jobs.to_json(os.path.join(data_dir, "linkedin_jobs.json"), orient="records", indent=2)

# Export to Excel
jobs.to_excel(os.path.join(data_dir, "linkedin_jobs.xlsx"), index=False)

print(f"\nFiles exported successfully to: {data_dir}")