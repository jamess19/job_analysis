import time, re, random
from typing import Dict, List, Optional, Iterable
from urllib.parse import urljoin, urlparse, urlsplit, urlunsplit, urlencode, parse_qsl

import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import platform

BASE = "https://www.vietnamworks.com"
if platform.system() == "Windows":
    USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/123.0.0.0 Safari/537.36")
else:
    USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/123.0.0.0 Safari/537.36")

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.vietnamworks.com/",
    "Connection": "keep-alive",
}

def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    retry = Retry(
        total=6, connect=3, read=3, status=6,
        backoff_factor=1.2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=50)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    try:
        s.get(BASE, timeout=20)
        time.sleep(0.6)
    except requests.RequestException:
        pass
    return s

def text(el) -> Optional[str]:
    if not el:
        return None
    t = el.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", t) if t else None

def smart_sleep(min_s=0.7, max_s=1.5):
    time.sleep(random.uniform(min_s, max_s))

def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    for attempt in range(1, 6):
        r = session.get(url, timeout=30)
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            wait = int(retry_after) if retry_after and retry_after.isdigit() else 5 * attempt
            wait += random.uniform(0.5, 1.5)
            print(f"[WARN] 429 {url} → ngủ {wait:.1f}s")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")
    r.raise_for_status()
    return BeautifulSoup("", "lxml")

# ---------- Paging helpers ----------
def with_page(url: str, page: int) -> str:
    if "{page}" in url:
        return url.format(page=page)
    if page <= 1:
        return url
    parts = urlsplit(url)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    q["page"] = str(page)
    new_query = urlencode(q, doseq=True)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

# ---------- Search page ----------
def _extract_jobs_from_next_data(soup: BeautifulSoup) -> List[Dict]:
    """
    Đọc JSON Next.js (__NEXT_DATA__) và cố gắng tìm mảng job để lấy đủ kết quả.
    """
    script = soup.select_one("script#__NEXT_DATA__")
    if not script or not script.string:
        return []
    try:
        data = json.loads(script.string)
    except Exception:
        return []

    def iter_lists(obj):
        if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
            yield obj
        elif isinstance(obj, dict):
            for v in obj.values():
                yield from iter_lists(v)

    results: List[Dict] = []
    for arr in iter_lists(data):
        keys = set().union(*(set(d.keys()) for d in arr)) if arr else set()
        if not keys:
            continue
        # Heuristic: list có dấu hiệu chứa job
        if not ({"id", "title"} <= keys or {"jobId", "jobTitle"} <= keys or any("job" in k.lower() for k in keys)):
            continue
        for d in arr:
            try:
                # Title
                title = d.get("jobTitle") or d.get("title") or d.get("name")

                # Company (can be str or dict)
                company_name = d.get("companyName") or d.get("employerName")
                comp_field = d.get("company")
                company_href = d.get("companyUrl")
                if isinstance(comp_field, dict):
                    company_name = company_name or comp_field.get("name")
                    company_href = company_href or comp_field.get("url")
                elif isinstance(comp_field, str):
                    company_name = company_name or comp_field

                # Job URL
                job_href = d.get("jobUrl") or d.get("url") or d.get("href") or d.get("seoUrl")
                if not job_href:
                    slug = d.get("slug") or d.get("jobSlug") or ""
                    jid = d.get("id") or d.get("jobId")
                    if slug and jid:
                        job_href = f"/{slug}-{jid}-jv"

                # Salary / Location / Experience
                salary = d.get("salary") or d.get("salaryDisplay") or d.get("salaryStr")
                location = d.get("location") or d.get("workPlace") or d.get("provinceName") or d.get("locations")
                if isinstance(location, list):
                    location = ", ".join([str(x) for x in location if x])
                exp = d.get("yearsOfExperience") or d.get("experience") or d.get("exp")

                if title and job_href:
                    results.append({
                        "title": title,
                        "job_url": urljoin(BASE, str(job_href)),
                        "company": company_name,
                        "company_url": urljoin(BASE, company_href) if company_href else None,
                        "salary_list": salary,
                        "address_list": location,
                        "exp_list": exp,
                    })
            except Exception:
                # Bỏ qua item hỏng để tránh vỡ toàn bộ trang
                continue
        if results:
            break
    return results

def parse_search_page(session: requests.Session, url: str, prefer_next: bool = True) -> List[Dict]:
    soup = get_soup(session, url)
    jobs: List[Dict] = []

    # Ưu tiên lấy từ __NEXT_DATA__ để có đủ job khi trang render bằng JS
    if prefer_next:
        jobs_from_next = _extract_jobs_from_next_data(soup)
        if jobs_from_next:
            return jobs_from_next

    # Thẻ card có thể thay đổi theo A/B test, liệt kê nhiều selector dự phòng
    cards = soup.select(
        "article.job-item, div.job-item, div.job-card, li.job, div.search-job, div.results div.job-item"
    )
    if not cards:
        # Fallback: link đến job detail thường có hậu tố -jv
        cards = [a.parent for a in soup.select("a[href*='-jv']")]

    for card in cards:
        a_title = None
        for css in [
            "a.job-title[href]", "h2 a[href*='-jv']", "h3 a[href*='-jv']",
            "a[href*='-jv']", "a[href*='/viec-lam/']"
        ]:
            a_title = card.select_one(css)
            if a_title:
                break
        if not a_title:
            continue

        title = text(a_title)
        job_url = urljoin(BASE, a_title.get("href"))

        comp_a = None
        for css in ["a[href*='/nha-tuyen-dung/']", "a[href*='/company']", ".company a[href]"]:
            comp_a = card.select_one(css)
            if comp_a:
                break
        company = text(comp_a) or text(card.select_one(".company, .company-name, .job-company"))
        company_url = urljoin(BASE, comp_a.get("href")) if comp_a and comp_a.has_attr("href") else None

        def pick_one(css_list):
            for c in css_list:
                el = card.select_one(c)
                if el and text(el):
                    return text(el)
            return None

        salary = pick_one([".salary", ".job-salary", "li.salary", ".tag-salary"])
        address = pick_one([".location", ".job-location", "li.location", ".address"])
        exp = pick_one([".experience", ".job-exp", "li.experience", "span[title*='Kinh nghiệm']"])

        jobs.append({
            "title": title,
            "job_url": job_url,
            "company": company,
            "company_url": company_url,
            "salary_list": salary,
            "address_list": address,
            "exp_list": exp,
        })
    return jobs

# ---------- Job detail ----------
def pick_info_value(soup: BeautifulSoup, label_keywords: Iterable[str]) -> Optional[str]:
    containers = [
        ".job-overview", ".job-summary", ".job-details", "section#job-details",
        ".job-attributes", ".job-info", ".job-meta"
    ]
    for css in containers:
        c = soup.select_one(css)
        if not c:
            continue
        for row in c.select("li, .row, .item, .info-item, .overview-item, .detail-item"):
            row_text = text(row) or ""
            label_el = row.find(["label", "strong", "b", "span"])
            label = (text(label_el) or "").lower()
            value = row_text
            if label_el:
                value = re.sub(re.escape(text(label_el) or ""), "", value, flags=re.I).strip(" :-–—")
            for kw in label_keywords:
                if kw.lower() in label or kw.lower() in row_text.lower():
                    m = re.split(r"[:：]", row_text, maxsplit=1)
                    if len(m) == 2:
                        return m[1].strip()
                    return value
    return None

def extract_deadline(soup: BeautifulSoup) -> Optional[str]:
    cand = soup.find(string=re.compile(r"Hạn nộp|Hết hạn|Deadline", re.I))
    if cand:
        m = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", cand)
        if m:
            return m.group(1)
    return pick_info_value(soup, ["Hạn nộp", "Hết hạn", "Deadline"])

def extract_tags(soup: BeautifulSoup):
    tags = []
    for css in [".tags a", ".job-tags a", "ul.tags a", ".skills a", ".tag-list a"]:
        tags.extend([text(a) for a in soup.select(css) if text(a)])
    return list(dict.fromkeys(tags))

def extract_desc_blocks(soup: BeautifulSoup):
    data = {}
    for h in soup.select("h2, h3"):
        ht = (text(h) or "").lower()
        if any(k in ht for k in ["mô tả công việc", "yêu cầu", "quyền lợi", "phúc lợi", "benefit"]):
            wrap = h.find_parent(class_=re.compile("section|block|desc|description|content")) or h.parent
            content = None
            if wrap:
                for cand in [wrap.select_one(".content, .description, .section-content, div"), h.find_next_sibling()]:
                    if cand and text(cand):
                        content = text(cand)
                        break
            if content:
                if "mô tả" in ht:
                    data["Mô tả công việc"] = content
                elif "yêu cầu" in ht:
                    data["Yêu cầu ứng viên"] = content
                elif "quyền lợi" in ht or "phúc lợi" in ht or "benefit" in ht:
                    data["Quyền lợi"] = content
    return data

def extract_company_link_from_job(soup: BeautifulSoup) -> Optional[str]:
    cand = soup.select_one("a[href*='/nha-tuyen-dung/']") or soup.select_one("a[href*='/company']")
    return urljoin(BASE, cand["href"]) if cand and cand.has_attr("href") else None

def scrape_job_detail(session: requests.Session, job_url: str) -> Dict:
    soup = get_soup(session, job_url)
    smart_sleep()

    title = text(soup.select_one("h1, .job-title, .job-detail h1"))
    salary = pick_info_value(soup, ["Mức lương", "Lương"])
    location = pick_info_value(soup, ["Địa điểm", "Nơi làm việc", "Làm việc tại"])
    experience = pick_info_value(soup, ["Kinh nghiệm"])
    deadline = extract_deadline(soup)
    tags = extract_tags(soup)
    desc_blocks = extract_desc_blocks(soup)
    company_url_detail = extract_company_link_from_job(soup)

    working_addresses = pick_info_value(soup, ["Địa điểm làm việc", "Nơi làm việc"])
    working_times = pick_info_value(soup, ["Thời gian làm việc", "Giờ làm việc", "Hình thức"])

    return {
        "detail_title": title,
        "detail_salary": salary,
        "detail_location": location,
        "detail_experience": experience,
        "deadline": deadline,
        "tags": "; ".join(tags) if tags else None,
        "desc_mota": desc_blocks.get("Mô tả công việc"),
        "desc_yeucau": desc_blocks.get("Yêu cầu ứng viên"),
        "desc_quyenloi": desc_blocks.get("Quyền lợi"),
        "working_addresses": working_addresses,
        "working_times": working_times,
        "company_url_from_job": company_url_detail,
    }

# ---------- Company page ----------
def scrape_company(session: requests.Session, company_url: Optional[str]) -> Dict:
    if not company_url:
        return {
            "company_name_full": None,
            "company_website": None,
            "company_size": None,
            "company_industry": None,
            "company_address": None,
            "company_description": None,
        }
    soup = get_soup(session, company_url)
    smart_sleep()

    company_name = None
    for css in ["h1", ".company-name h1", "meta[property='og:title']", "title"]:
        el = soup.select_one(css)
        if el:
            company_name = el.get("content") if el.name == "meta" else text(el)
            if company_name:
                break

    website = size = industry = address = None
    containers = [
        "div.company-profile", "div.company-info", "section#company", "div.company-overview",
        "div#company-info", "div.company-content", "div.company-intro"
    ]
    container = None
    for css in containers:
        c = soup.select_one(css)
        if c:
            container = c
            break
    if container is None:
        container = soup

    rows = container.select("li, .row, .item, .info-item, .company-info-item, dl, .d-flex")
    for row in rows:
        row_text = text(row) or ""
        label = None
        value = None
        strong = row.find(["strong", "b", "label", "dt", "span"])
        if strong:
            label = text(strong)
            value = row_text
            if label:
                value = re.sub(re.escape(label), "", value, flags=re.I).strip(" :-–—")
        else:
            m = re.match(r"^([^:：]+)[:：]\s*(.+)$", row_text)
            if m:
                label, value = m.group(1).strip(), m.group(2).strip()

        if not label or not value:
            continue

        ln = re.sub(r"\s+", " ", label.lower())
        if "website" in ln or "trang web" in ln:
            website = value
        elif "quy mô" in ln or "size" in ln or "nhân sự" in ln:
            size = value
        elif "lĩnh vực" in ln or "industry" in ln or "ngành" in ln:
            industry = value
        elif "địa chỉ" in ln or "address" in ln or "trụ sở" in ln:
            address = value

    description = None
    for css in [
        "div.company-description", "#readmore-company", "#company-description",
        "section.company-description", "div.description", "div#readmore-content"
    ]:
        el = soup.select_one(css)
        if el and text(el):
            description = text(el)
            break

    return {
        "company_name_full": company_name,
        "company_website": website,
        "company_size": size,
        "company_industry": industry,
        "company_address": address,
        "company_description": description,
    }

# ---------- Pipeline ----------
def crawl_list_url_to_dataframe(list_url_page1: str, start_page: int = 1, end_page: int = 1,
                                delay_between_pages=(0.6, 1.2),
                                prefer_next: bool = True,
                                fetch_company: bool = True) -> pd.DataFrame:
    rows: List[Dict] = []
    seen_jobs = set()
    s = build_session()

    for page in range(start_page, end_page + 1):
        url = with_page(list_url_page1, page)
        print(f"[INFO] Crawling search page {page}: {url}")
        jobs = parse_search_page(s, url, prefer_next=prefer_next)
        if not jobs:
            print(f"[INFO] Trang {page} không còn job — dừng sớm.")
            break

        for j in jobs:
            job_url = j["job_url"]
            job_id = urlparse(job_url).path
            if job_id in seen_jobs:
                continue
            seen_jobs.add(job_id)

            # Job detail
            try:
                detail = scrape_job_detail(s, job_url)
            except Exception as e:
                print(f"[WARN] Lỗi job detail {job_url}: {e}")
                detail = {k: None for k in [
                    "detail_title", "detail_salary", "detail_location",
                    "detail_experience", "deadline", "tags", "desc_mota",
                    "desc_yeucau", "desc_quyenloi", "working_addresses",
                    "working_times", "company_url_from_job"
                ]}

            # Company detail (tùy chọn)
            comp = {k: None for k in [
                "company_name_full", "company_website", "company_size",
                "company_industry", "company_address", "company_description"
            ]}
            if fetch_company:
                company_url = detail.get("company_url_from_job") or j.get("company_url")
                try:
                    comp = scrape_company(s, company_url)
                except Exception as e:
                    print(f"[WARN] Lỗi company {company_url}: {e}")

            row = {**j, **detail, **comp}
            rows.append(row)

        smart_sleep(*delay_between_pages)

    df = pd.DataFrame(rows)
    cols = [
        "title", "detail_title",
        "job_url",
        "company", "company_name_full",
        "company_url", "company_url_from_job",
        "salary_list", "detail_salary",
        "address_list", "detail_location",
        "exp_list", "detail_experience",
        "deadline", "tags",
        "working_addresses", "working_times",
        "desc_mota", "desc_yeucau", "desc_quyenloi",
        "company_website", "company_size", "company_industry",
        "company_address", "company_description",
    ]
    cols = [c for c in cols if c in df.columns]
    return df.loc[:, cols] if cols else df

def crawl_many_lists(list_urls: Iterable[str], start_page: int = 1, end_page: int = 1,
                     delay_between_pages=(0.6, 1.2), sleep_between_lists=(0.8, 1.6),
                     prefer_next: bool = True, fetch_company: bool = True) -> pd.DataFrame:
    all_frames: List[pd.DataFrame] = []
    for url in list_urls:
        df_one = crawl_list_url_to_dataframe(
            url, start_page, end_page, delay_between_pages,
            prefer_next=prefer_next, fetch_company=fetch_company
        )
        if not df_one.empty:
            all_frames.append(df_one)
        smart_sleep(*sleep_between_lists)
    if not all_frames:
        return pd.DataFrame()
    df = pd.concat(all_frames, ignore_index=True)
    if "job_url" in df.columns:
        df = df.drop_duplicates(subset=["job_url"])
    return df

if __name__ == "__main__":
    import argparse, os
    parser = argparse.ArgumentParser(description="Crawl VietnamWorks jobs (schema như TopCV/CareerViet) và lưu CSV/XLSX.")
    parser.add_argument("--list-urls", "-u", nargs="+", required=True,
                        help="URL danh mục trang 1 hoặc template có {page}. VD: https://www.vietnamworks.com/viec-lam?q=backend")
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--end-page", type=int, default=1)
    parser.add_argument("--out-prefix", default="../data-files/vietnamworks_it_jobs", help="Prefix file đầu ra (không kèm đuôi).")
    parser.add_argument("--no-company", action="store_true", help="Bỏ crawl trang công ty (tránh 404/yêu cầu đăng nhập).")
    parser.add_argument("--no-next", action="store_true", help="Không đọc __NEXT_DATA__, chỉ parse HTML.")
    args = parser.parse_args()

    print(f"[INFO] Crawling {len(args.list_urls)} danh mục | pages {args.start_page}..{args.end_page}")
    df = crawl_many_lists(
        args.list_urls,
        start_page=args.start_page,
        end_page=args.end_page,
        prefer_next=not args.no_next,
        fetch_company=not args.no_company,
    )

    os.makedirs(os.path.dirname(args.out_prefix), exist_ok=True)
    out_csv = f"{args.out_prefix}_combined.csv"
    out_xlsx = f"{args.out_prefix}_combined.xlsx"

    print(df.head())
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    try:
        df.to_excel(out_xlsx, index=False)
    except Exception as e:
        print(f"[WARN] XLSX write failed: {e}")
    print(f"[OK] Saved: {out_csv}")