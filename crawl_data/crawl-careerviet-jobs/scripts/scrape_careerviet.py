import time
import re
import random
from typing import Dict, List, Optional, Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

BASE = "https://careerviet.vn"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/123.0.0.0 Safari/537.36"),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://careerviet.vn/",
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
    import re as _re
    t = el.get_text(" ", strip=True)
    return _re.sub(r"\s+", " ", t) if t else None

def smart_sleep(min_s=0.6, max_s=1.4):
    time.sleep(random.uniform(min_s, max_s))

def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    for attempt in range(1, 6):
        r = session.get(url, timeout=30)
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            if retry_after:
                try:
                    wait = int(retry_after)
                except ValueError:
                    wait = 5 * attempt
            else:
                wait = 5 * attempt
            wait += random.uniform(0.5, 1.5)
            print(f"[WARN] 429 tại {url} → ngủ {wait:.1f}s (attempt {attempt})")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")
    r.raise_for_status()
    return BeautifulSoup("", "lxml")

# ---------- Paging helpers ----------
def build_paged_url(list_url_page1: str, page: int) -> str:
    """
    CareerViet page 2 mẫu: https://careerviet.vn/viec-lam/ai-k-trang-2-vi.html
    Quy tắc: chèn '-trang-{page}-' trước 'vi.html'. Trang 1 giữ nguyên URL gốc.
    """
    if page <= 1:
        return list_url_page1
    # Thay ...-vi.html -> ...-trang-{page}-vi.html
    return re.sub(r"-vi\.html$", f"-trang-{page}-vi.html", list_url_page1)

# ---------- Search page ----------
def parse_search_page(session: requests.Session, url: str) -> List[Dict]:
    soup = get_soup(session, url)
    jobs: List[Dict] = []

    # Nhiều bố cục khả dĩ, thử lần lượt
    cards = soup.select(
        "div.job-item, div.job-item-list, div.job, li.job, div#jobs-found div.job-item"
    )
    if not cards:
        # Fallback: bất kỳ thẻ có link tới trang job detail
        cards = [a.parent for a in soup.select("a[href*='/vi/tim-viec-lam/']")]

    for card in cards:
        a_title = None
        for css in [
            "a.job_link[href]",
            "h2 a[href*='/vi/tim-viec-lam/']",
            "h3 a[href*='/vi/tim-viec-lam/']",
            "a[href*='/vi/tim-viec-lam/']",
        ]:
            a_title = card.select_one(css)
            if a_title:
                break
        if not a_title:
            continue

        title = text(a_title)
        job_url = urljoin(BASE, a_title.get("href"))

        comp_a = None
        for css in [
            "a[href*='/vi/nha-tuyen-dung/']",
            ".company a[href]",
            "a.company[href]",
        ]:
            comp_a = card.select_one(css)
            if comp_a:
                break
        company = text(comp_a) if comp_a else text(card.select_one(".company, .job-company"))
        company_url = urljoin(BASE, comp_a.get("href")) if comp_a and comp_a.has_attr("href") else None

        # Thông tin tóm tắt (có thể rải rác)
        salary = None
        for css in [".salary", ".job-salary", ".content-salary", ".tag-salary", "li.salary"]:
            el = card.select_one(css)
            if el and text(el):
                salary = text(el)
                break

        address = None
        for css in [".location", ".job-location", ".content-location", ".work-location", "li.location"]:
            el = card.select_one(css)
            if el and text(el):
                address = text(el)
                break

        exp = None
        for css in [".experience", ".job-exp", "li.experience", "li:contains('Kinh nghiệm')"]:
            el = card.select_one(css) if ":contains" not in css else None
            if el and text(el):
                exp = text(el)
                break

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
    """
    Quét các vùng 'thông tin công việc' để tìm giá trị theo nhãn (VD: Mức lương/Địa điểm/Kinh nghiệm).
    """
    # Các khối khả dĩ chứa key-value
    containers = [
        "ul.job-info", ".job-summary", ".job-attributes", ".job-detail", ".section-content", "div#job-summary"
    ]
    for css in containers:
        container = soup.select_one(css)
        if not container:
            continue
        for row in container.select("li, .row, .item, .info-item"):
            row_text = text(row) or ""
            label_el = None
            for lab_css in ["label", "span.label", "span.lbl", "strong", "b"]:
                label_el = row.select_one(lab_css)
                if label_el:
                    break
            label = (text(label_el) or "").lower()
            value = row_text
            if label:
                value = re.sub(re.escape(text(label_el) or ""), "", value).strip(" :-–—")
            for kw in label_keywords:
                if kw.lower() in label or kw.lower() in row_text.lower():
                    # Làm sạch value lần nữa
                    m = re.split(r"[:：]", row_text, maxsplit=1)
                    if len(m) == 2:
                        value = m[1].strip()
                    return value
    return None

def extract_deadline(soup: BeautifulSoup) -> Optional[str]:
    # BeautifulSoup deprecates 'text' in favor of 'string'
    cand = soup.find(string=re.compile(r"Hạn nộp|Hết hạn|Deadline", re.I))
    if cand:
        m = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", cand)
        if m:
            return m.group(1)
    # Tìm quanh các nhãn giống pick_info_value
    return pick_info_value(soup, ["Hạn nộp", "Hết hạn", "Deadline"])

def extract_tags(soup: BeautifulSoup):
    tags = []
    for css in [".tags a", ".job-tags a", "ul.tags a", ".skills a", ".tag-list a"]:
        tags.extend([text(a) for a in soup.select(css) if text(a)])
    return list(dict.fromkeys(tags))

def extract_desc_blocks(soup: BeautifulSoup):
    """
    Tìm các mục mô tả theo heading 'Mô tả Công việc', 'Yêu Cầu Công Việc', 'Quyền lợi/Phúc lợi'
    """
    data = {}
    sections = []
    for h in soup.select("h2, h3"):
        ht = (text(h) or "").lower()
        if any(k in ht for k in ["mô tả công việc", "yêu cầu công việc", "quyền lợi", "phúc lợi"]):
            # Lấy sibling/parent container
            wrap = h.find_parent(class_=re.compile("section|block|desc|description")) or h.parent
            content = None
            if wrap:
                # Tìm vùng text ngay sau heading
                for cand in [wrap.select_one("div, .content, .section-content, .description"), h.find_next_sibling()]:
                    if cand and text(cand):
                        content = text(cand)
                        break
            if not content:
                # Fallback: gom các <li> dưới heading
                lis = []
                nxt = h.find_next()
                while nxt and nxt.name in ("ul", "ol", "p", "li") and len(" ".join(lis)) < 5000:
                    if text(nxt):
                        lis.append(text(nxt))
                    nxt = nxt.find_next_sibling()
                content = " ".join(lis) if lis else None
            if content:
                if "mô tả" in ht:
                    data["Mô tả công việc"] = content
                elif "yêu cầu" in ht:
                    data["Yêu cầu ứng viên"] = content
                elif "quyền lợi" in ht or "phúc lợi" in ht:
                    data["Quyền lợi"] = content
    return data

def extract_company_link_from_job(soup: BeautifulSoup) -> Optional[str]:
    cand = soup.select_one("a[href*='/vi/nha-tuyen-dung/']")
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

    # Địa điểm/thời gian làm việc nếu có khối riêng
    working_addresses = None
    for lab in ["Địa điểm làm việc", "Nơi làm việc"]:
        val = pick_info_value(soup, [lab])
        if val:
            working_addresses = val
            break

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

    # Tên công ty
    company_name = None
    for css in ["h1", ".company-name h1", "meta[property='og:title']", "title"]:
        el = soup.select_one(css)
        if el:
            company_name = el.get("content") if el.name == "meta" else text(el)
            if company_name:
                break

    website = size = industry = address = None
    # Tập container có thể chứa thông tin
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
                                delay_between_pages=(0.5, 1.0)) -> pd.DataFrame:
    rows: List[Dict] = []
    seen_jobs = set()
    s = build_session()

    for page in range(start_page, end_page + 1):
        url = build_paged_url(list_url_page1, page)
        print(f"[INFO] Crawling search page {page}: {url}")
        jobs = parse_search_page(s, url)
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

            company_url = detail.get("company_url_from_job") or j.get("company_url")

            # Company detail
            try:
                comp = scrape_company(s, company_url)
            except Exception as e:
                print(f"[WARN] Lỗi company {company_url}: {e}")
                comp = {k: None for k in [
                    "company_name_full", "company_website", "company_size",
                    "company_industry", "company_address", "company_description"
                ]}

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
                     delay_between_pages=(0.5, 1.0), sleep_between_lists=(0.8, 1.6)) -> pd.DataFrame:
    all_frames: List[pd.DataFrame] = []
    for url in list_urls:
        df_one = crawl_list_url_to_dataframe(url, start_page, end_page, delay_between_pages)
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
    parser = argparse.ArgumentParser(description="Crawl CareerViet jobs (giữ nguyên schema như TopCV) và lưu CSV/XLSX.")
    parser.add_argument("--list-urls", "-u", nargs="+", required=False, default=[
        "https://careerviet.vn/viec-lam/ai-k-vi.html",
        "https://careerviet.vn/viec-lam/backend-k-vi.html",
        "https://careerviet.vn/viec-lam/cntt-phan-mem-c1-vi.html",
    ], help="URL danh mục trang 1. VD: -u https://careerviet.vn/viec-lam/ai-k-vi.html")
    parser.add_argument("--start-page", type=int, default=1, help="CareerViet trang tối đa thường là 1")
    parser.add_argument("--end-page", type=int, default=1, help="Nếu >=2 sẽ dùng dạng -trang-{page}-vi.html")
    parser.add_argument("--out-prefix", default="../data-files/careerviet_it_jobs", help="Prefix file đầu ra (không kèm đuôi).")
    args = parser.parse_args()

    print(f"[INFO] Crawling {len(args.list_urls)} danh mục | pages {args.start_page}..{args.end_page}")
    df = crawl_many_lists(args.list_urls, start_page=args.start_page, end_page=args.end_page)

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