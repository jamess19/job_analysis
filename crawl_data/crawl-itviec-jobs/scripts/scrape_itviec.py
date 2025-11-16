import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import json
import pandas as pd
import csv
# Headers giả lập browser
def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/124.0.0.0 Safari/537.36"
    }

# Lấy số trang tối đa
def get_max_page(keyword, location):
    q = urllib.parse.quote(keyword)
    loc = urllib.parse.quote(location)
    url = f"https://itviec.com/it-jobs/{q}/{loc}"
    resp = requests.get(url, headers=get_headers())
    soup = BeautifulSoup(resp.text, "html.parser")
    pages = soup.select("ul.pagination li a")
    if not pages:
        return 1
    try:
        return max(int(p.text.strip()) for p in pages if p.text.strip().isdigit())
    except:
        return 1

# Lấy danh sách link job theo từ khóa + địa điểm
def get_job_list(keyword, location):
    keyword = keyword.replace(" ", "-").lower().strip()
    location = location.replace(" ", "-").lower().strip()
    if(location == "ho-chi-minh"):
        location+="-hcm"
    job_links = []
    max_page = get_max_page(keyword, location)
    print(f"Found {max_page} pages for {keyword} in {location}")

    for page in range(1, max_page + 1):
        list_url = f"https://itviec.com/it-jobs/{keyword}/{location}?page={page}"
        response = requests.get(list_url, headers=get_headers())
        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        job_items = soup.find_all("div", {"data-controller": "search--job-selection"})
        for job_item in job_items:
            try:
                title_elem = job_item.find("h3", {"data-search--job-selection-target": "jobTitle"})
                if not title_elem or not title_elem.has_attr("data-url"):
                    continue
                # Lấy trực tiếp data-url
                job_links.append(title_elem["data-url"])
            except Exception as e:
                print(f"Error scraping job link on page {page}: {e}")
                continue

        time.sleep(random.uniform(3, 7))

    return job_links

# Lấy chi tiết job từ từng link
def scrape_job_detail(job_url: str) -> dict:
    job_post = {
        "title": None,
        "detail_title": None,
        "job_url": job_url,
        "company": None,
        "company_name_full": None,
        "company_url": None,
        "company_url_from_job": None,
        "salary_list": None,
        "detail_salary": None,
        "address_list": None,
        "detail_location": None,
        "exp_list": None,
        "detail_experience": None,
        "deadline": None,
        "working_addresses": None,
        "working_times": None,
        "desc_mota": None,
        "desc_yeucau": None,
        "desc_quyenloi": None,
        "company_website": None,
        "company_size": None,
        "company_industry": None,
        "company_address": None,
        "company_description": None,
    }

    try:
        job_detail = requests.get(job_url, headers=get_headers())
        if job_detail.status_code != 200:
            print(f"[WARN] Failed to fetch job details for {job_url}")
            return job_post

        job_soup = BeautifulSoup(job_detail.text, "html.parser")

        # Thông tin job
        job_post["title"] = job_soup.select_one("div.job-header-info h1").get_text(strip=True)
        job_post["detail_title"] = job_post["title"]
        job_post["detail_salary"] = "Login to view"
        
        # wwork Location
        job_post["detail_location"] = job_soup.select_one("div.imb-3 span.normal-text").get_text(strip=True)
        job_post["address_list"] = [job_post["detail_location"]] if job_post["detail_location"] else None
        job_post["working_addresses"] = job_post["detail_location"]
        job_post["working_times"] = ""

        # Skill require
        tags = [a.get_text(strip=True) for a in job_soup.select("div:has(> .fw-600:-soup-contains('Skills')) a")]
        job_post["skills"] = ", ".join(tags) if tags else None
        job_post["exp_list"] = [job_post["detail_experience"]] if job_post["detail_experience"] else None


        desc_sections = job_soup.find_all("div", class_="job-description__item--content")
        job_post["desc_mota"] = desc_sections[0].text.strip() if len(desc_sections) > 0 else ""
        job_post["desc_yeucau"] = desc_sections[1].text.strip() if len(desc_sections) > 1 else ""
        job_post["desc_quyenloi"] = desc_sections[2].text.strip() if len(desc_sections) > 2 else ""

        # Thông tin công ty
        job_post["company_name_full"] = job_soup.find("h2", class_="employer-long-overview__name").text.strip() if job_soup.find("h2", class_="employer-long-overview__name") else None

        company_link_elem = job_soup.find("a", class_="employer-long-overview__info")
        job_post["company_url"] = "https://itviec.com" + company_link_elem["href"] if company_link_elem else None

        # Scrape company page nếu có link
        if job_post["company_url"]:
            comp_resp = requests.get(job_post["company_url"], headers=get_headers())
            if comp_resp.status_code == 200:
                comp_soup = BeautifulSoup(comp_resp.text, "html.parser")
                job_post["company_website"] = comp_soup.find("a", {"rel": "nofollow noopener noreferrer"})["href"] if comp_soup.find("a", {"rel": "nofollow noopener noreferrer"}) else ""
                job_post["company_size"] = comp_soup.find("svg", class_="fi-rr-users-alt").parent.parent.text.strip() if comp_soup.find("svg", class_="fi-rr-users-alt") else ""
                job_post["company_industry"] = comp_soup.find("svg", class_="fi-rr-briefcase").parent.parent.text.strip() if comp_soup.find("svg", class_="fi-rr-briefcase") else ""
                job_post["company_address"] = comp_soup.find("svg", class_="fi-rr-marker").parent.parent.text.strip() if comp_soup.find("svg", class_="fi-rr-marker") else ""
                job_post["company_description"] = comp_soup.find("div", class_="employer-overview__description").text.strip() if comp_soup.find("div", class_="employer-overview__description") else ""

        time.sleep(random.uniform(2, 5))
    except Exception as e:
        print(f"[ERROR] scrape_job_detail({job_url}): {e}")

    return job_post

# Export functions
def export_to_json(data):
    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def export_to_csv(data):
    if data:
        fields = data[0].keys()
        with open('jobs.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)

def export_to_excel(data):
    df = pd.DataFrame(data)
    df.to_excel('jobs.xlsx', index=False)

def scrape_data(keyword, location):
    print(f"🔎 Đang crawl danh sách job cho '{keyword}' tại '{location}'...")
    job_links = get_job_list(keyword, location)
    print(f"✅ Tìm thấy {len(job_links)} job. Đang scrape chi tiết...")

    jobs_data = []
    for i, job_url in enumerate(job_links, 1):
        print(f"[{i}/{len(job_links)}] Scraping {job_url}")
        detail = scrape_job_detail(job_url)
        jobs_data.append(detail)

    return jobs_data

# Main execution
if __name__ == "__main__":
    print("Scraping job list...")
    jobs_data = scrape_data("software engineer", "Ho Chi Minh")
    export_to_json(jobs_data)
    export_to_csv(jobs_data)
    export_to_excel(jobs_data)
    print("Scraping completed. Files generated: jobs.json, jobs.csv, jobs.xlsx")