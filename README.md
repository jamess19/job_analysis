# Job Analysis - Hệ thống Thu thập và Phân tích Dữ liệu Việc làm

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Platform Support](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Job Analysis** là một hệ thống tự động thu thập, phân tích và xuất báo cáo dữ liệu việc làm từ các nền tảng tuyển dụng hàng đầu tại Việt Nam. Dự án được phát triển như Khóa Luận Tốt Nghiệp (KLTN) cho việc phân tích thị trường nhân lực.

## Mục Lục

- [Tính Năng Chính](#tính-năng-chính)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt](#cài-đặt)
- [Cách Sử Dụng](#cách-sử-dụng)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Nền Tảng Được Hỗ Trợ](#nền-tảng-được-hỗ-trợ)
- [Định Dạng Dữ Liệu](#định-dạng-dữ-liệu)
- [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
- [Xử Lý Lỗi Và An Toàn](#xử-lý-lỗi-và-an-toàn)
- [Đóng Góp](#đóng-góp)
- [Giấy Phép](#giấy-phép)

---

## Tính Năng Chính

### 1. **Thu Thập Dữ Liệu Đa Nền Tảng**
- **LinkedIn**: Thu thập thông tin việc làm từ LinkedIn toàn cầu
- **VietnamWorks**: Tích hợp scraper cho nền tảng VietnamWorks
- **ITViec**: Thu thập dữ liệu công nghệ từ ITViec
- **CareerViet**: Scraper cho nền tảng CareerViet
- **TopCV**: Phân tích chi tiết và trích xuất dữ liệu từ TopCV

### 2. **Trích Xuất Thông Tin Chi Tiết**
Mỗi bài đăng việc làm được phân tích để trích xuất:
- 📋 **Thông tin cơ bản**: Chức danh, công ty, địa điểm, mức lương
- 📝 **Mô tả công việc**: Danh sách chi tiết các nhiệm vụ
- ⚙️ **Yêu cầu**: Phân chia thành "bắt buộc" và "tốt có"
- 🎁 **Phúc lợi**: Danh sách các lợi ích công việc
- 📍 **Địa điểm làm việc**: Chi tiết vị trí và loại hình làm việc
- ⏰ **Thời gian làm việc**: Thông tin về giờ làm việc

### 3. **Xuất Dữ Liệu Linh Hoạt**
- 📊 **JSON**: Định dạng có cấu trúc đầy đủ cho lập trình
- 📈 **CSV**: Định dạng bảng tính cho Excel/Google Sheets
- 📋 **XLSX**: File Excel với định dạng chuyên nghiệp
- 📄 **TXT**: Báo cáo phân tích có định dạng tiếng Việt

### 4. **Phân Tích Tự Động**
- Tạo báo cáo chi tiết cho từng bài đăng
- Tổng hợp báo cáo từ nhiều bài đăng
- Định dạng báo cáo tiếng Việt chuyên nghiệp
- Ghi lại metadata (thời gian trích xuất, nguồn gốc)

### 5. **Tính Năng An Toàn Nâng Cao**
- 🤖 **Bypass Bot Detection**: Sử dụng undetected-chromedriver
- 🎭 **User Agent Rotation**: Xoay vòng random user agents
- ⏱️ **Rate Limiting**: Thêm độ trễ ngẫu nhiên giữa các request
- 🔄 **Retry Logic**: Tự động thử lại khi gặp lỗi
- 🌐 **Connection Pooling**: Quản lý kết nối hiệu quả

### 6. **Hỗ Trợ Đa Nền Tảng**
- ✅ Windows (Có user agent cụ thể)
- ✅ macOS (Có user agent cụ thể)
- ✅ Linux (Support cơ bản)

---

## Yêu Cầu Hệ Thống

### Yêu Cầu Bắt Buộc
- **Python**: 3.8 hoặc cao hơn
- **pip**: Trình quản lý gói Python
- **Chrome/Chromium**: Cho Selenium automation (tự động tải nếu cần)
- **RAM**: Tối thiểu 2GB cho browser automation
- **Kết nối Internet**: Bắt buộc để scrape dữ liệu

### Yêu Cầu Tùy Chọn
- **Excel**: Nếu muốn mở file XLSX
- **Text Editor/IDE**: Để chỉnh sửa code

---

## Cài Đặt

### Bước 1: Clone Repository
```bash
git clone <repository-url>
cd job_analysis
```

### Bước 2: Tạo Virtual Environment (Khuyến Nghị)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 3: Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Kiểm Tra Cài Đặt
```bash
python -c "import selenium; import beautifulsoup4; print('Cài đặt thành công!')"
```

---

## Cách Sử Dụng

### 1. **Sử Dụng Enhanced Job Collector (Chính)**

Đây là công cụ chính để thu thập và phân tích dữ liệu từ TopCV:

```bash
python enhanced_job_collector.py
```

**Quy trình tương tác:**
```
Nhập chức danh/vị trí tìm kiếm (VD: "Software Engineer"):
Nhập cấp độ công việc (tùy chọn):
Nhập địa điểm (tùy chọn):
Nhập lĩnh vực/ngành (tùy chọn):
```

**Đầu ra:**
- `collected_jobs_<timestamp>.json` - Dữ liệu thô của 5 bài đăng
- `job_analysis_1_<timestamp>.txt` - Báo cáo chi tiết từng bài
- `combined_analysis_<timestamp>.txt` - Báo cáo tổng hợp

### 2. **Test Enhanced Collector**

```bash
python test_fixed_collector.py
```

Tìm kiếm "Software Engineer" tự động và tạo báo cáo phân tích.

### 3. **Scrape LinkedIn**

```bash
python crawl_data/crawl-linkedin-jobs/scripts/scrape_linkedin.py
```

**Tính năng:**
- Selenium-based scraping
- Trích xuất job IDs và chi tiết công ty
- Export JSON/CSV/XLSX
- Bypass anti-bot detection

### 4. **Scrape VietnamWorks**

```bash
python crawl_data/crawl-vietnamwork-jobs/scripts/scrape_vietnamwork.py \
  -u "https://www.vietnamworks.com/viec-lam?q=backend&g=5" \
  --start-page 1 --end-page 2
```

**Tham số:**
- `-u, --url`: URL trang tìm kiếm
- `--start-page`: Trang bắt đầu (mặc định: 1)
- `--end-page`: Trang kết thúc (mặc định: 1)

### 5. **Scrape ITViec**

```bash
python crawl_data/crawl-itviec-jobs/scripts/scrape_itviec.py \
  --list-urls "https://itviec.com/it-jobs/backend" \
  --start-page 1 --end-page 3
```

**Tham số:**
- `--list-urls`: URL trang tìm kiếm
- `--start-page`: Trang bắt đầu
- `--end-page`: Trang kết thúc

### 6. **Scrape CareerViet**

```bash
python crawl_data/crawl-careerviet-jobs/scripts/scrape_careerviet.py \
  -u "https://careerviet.vn/viec-lam/cntt-phan-mem-c1-vi.html" \
  --start-page 1 --end-page 1
```

---

## Cấu Trúc Dự Án

```
job_analysis/
│
├── 📄 README.md                           # File này
├── 📋 requirements.txt                    # Danh sách dependencies
├── 📝 pyproject.toml                      # Cấu hình Python project
│
├── 🐍 enhanced_job_collector.py           # Công cụ chính (550 dòng)
│                                          # Scrape TopCV + phân tích
│
├── 🧪 test_fixed_collector.py             # Script test
│
├── 📁 collected_job_data/                 # Thư mục đầu ra
│   ├── collected_jobs_*.json              # Dữ liệu thô JSON
│   ├── job_analysis_*.txt                 # Báo cáo từng bài
│   └── combined_analysis_*.txt            # Báo cáo tổng hợp
│
└── 📁 crawl_data/                         # Crawlers cho từng nền tảng
    │
    ├── 📂 crawl-linkedin-jobs/
    │   ├── scripts/
    │   │   ├── scrape_linkedin.py         # Selenium-based scraper
    │   │   └── scape_linkedin_v2.py       # JobSpy-based alternative
    │   ├── data-files/                    # Output CSV/JSON/XLSX
    │   └── README.md
    │
    ├── 📂 crawl-vietnamwork-jobs/
    │   ├── scripts/
    │   │   └── scrape_vietnamwork.py      # BeautifulSoup-based
    │   ├── data-files/
    │   └── README.md
    │
    ├── 📂 crawl-itviec-jobs/
    │   ├── scripts/
    │   │   └── scrape_itviec.py           # Multi-page scraper
    │   ├── data-files/
    │   │   ├── jobs.json
    │   │   ├── jobs.csv
    │   │   └── jobs.xlsx
    │   └── README.md
    │
    ├── 📂 crawl-careerviet-jobs/
    │   ├── scripts/
    │   │   └── scrape_careerviet.py
    │   ├── data-files/
    │   └── README.md
    │
    └── 📁 data-files/                     # Dữ liệu tập trung từ tất cả crawlers
```

---

## Nền Tảng Được Hỗ Trợ

| Nền Tảng | Crawler | Phương Pháp | Trạng Thái |
|----------|---------|-----------|----------|
| **LinkedIn** | `scrape_linkedin.py` | Selenium | ✅ Hoạt động |
| **VietnamWorks** | `scrape_vietnamwork.py` | BeautifulSoup + Requests | ✅ Hoạt động |
| **ITViec** | `scrape_itviec.py` | Requests + BeautifulSoup | ✅ Hoạt động |
| **CareerViet** | `scrape_careerviet.py` | BeautifulSoup + Requests | ✅ Hoạt động |
| **TopCV** | `enhanced_job_collector.py` | Selenium | ✅ Hoạt động |

---

## Định Dạng Dữ Liệu

### JSON Output Sample

```json
{
  "url": "https://www.topcv.vn/viec-lam/java-developer/1753320.html",
  "extracted_at": "2025-07-15T21:48:44.312617",
  "title": "Java Developer",
  "company": "NINA Company",
  "location": "Ho Chi Minh",
  "salary": "4 - 12 triệu",
  "job_description": [
    "Develop Java applications",
    "Work with Spring Boot",
    "Code review and testing"
  ],
  "must_have_requirements": [
    "2+ years Java experience",
    "Knowledge of Spring Framework",
    "English communication"
  ],
  "nice_to_have_requirements": [
    "Kubernetes experience",
    "Docker knowledge"
  ],
  "benefits": [
    "Competitive salary",
    "Health insurance",
    "Flexible working hours"
  ],
  "work_location": "Floor 5, Building A, HCM",
  "work_time": "8:30 AM - 5:30 PM"
}
```

### TXT Report Sample

```
========================================
BÁNG CÁO PHÂN TÍCH CÔNG VIỆC
========================================

🔗 Nguồn: https://www.topcv.vn/viec-lam/java-developer/1753320.html
📅 Trích xuất lúc: 2025-07-15 21:48:44

📋 THÔNG TIN CHUNG
  Chức danh: Java Developer
  Công ty: NINA Company
  Địa điểm: Ho Chi Minh
  Mức lương: 4 - 12 triệu

📝 MÔ TẢ CÔNG VIỆC
  • Develop Java applications
  • Work with Spring Boot
  • Code review and testing

⚙️ YÊU CẦU BẮTBUỘC
  • 2+ years Java experience
  • Knowledge of Spring Framework
  • English communication

✨ YÊU CẦU TỐTHAVING
  • Kubernetes experience
  • Docker knowledge

🎁 PHÚCLỢI
  • Competitive salary
  • Health insurance
  • Flexible working hours

📍 ĐỊA ĐIỂM LÀM VIỆC
  Floor 5, Building A, HCM

⏰ THỜI GIAN LÀM VIỆC
  8:30 AM - 5:30 PM
========================================
```

---

## Công Nghệ Sử Dụng

### Web Scraping & Automation
```
selenium (>=4.0.0)                    # Browser automation
beautifulsoup4 (>=4.13.5)             # HTML/XML parsing
lxml (>=6.0.1)                        # Fast XML processing
requests (>=2.32.4)                   # HTTP requests
undetected-chromedriver (>=3.5.0)     # Bypass anti-bot
webdriver-manager (>=4.0.0)           # ChromeDriver management
fake-useragent (>=1.4.0)              # User agent rotation
jobspy (>=2.0.0)                      # Multi-site job scraper
```

### Data Processing & Export
```
pandas (>=2.1.0)                      # Data manipulation
openpyxl (>=3.1.5)                    # Excel generation
urllib3 (>=2.2.3)                     # Connection pooling
```

### Built-in Libraries
```
json, re, time, random, logging, datetime, csv, os, argparse, pathlib, typing
```

---

## Xử Lý Lỗi Và An Toàn

### Cơ Chế Bảo Vệ

1. **Bypass Anti-Bot Detection**
   - Sử dụng `undetected-chromedriver` để vượt qua CAPTCHAs
   - Tắt automation detection flags
   - No-sandbox mode cho environments hạn chế

2. **User Agent Rotation**
   - Random user agents cho mỗi request
   - Platform-specific agents (Windows, macOS, Linux)

3. **Rate Limiting**
   - Độ trễ ngẫu nhiên 3-8 giây giữa requests
   - Tránh quá tải server

4. **Retry Logic**
   - Tự động thử lại khi gặp timeout
   - Exponential backoff strategy

5. **Session Management**
   - Connection pooling với urllib3
   - Persistent cookies cho requests

### Xử Lý Ngoại Lệ

```python
try:
    # Scraping operations
except TimeoutException:
    # Handle timeout
except NoSuchElementException:
    # Handle missing element
except Exception as e:
    # Logging và recovery
```

---

## Cách Hoạt Động Của Enhanced Collector

### Quy Trình Chính:

1. **Nhập Tiêu Chí Tìm Kiếm**
   - Chức danh/vị trí
   - Cấp độ công việc (tùy chọn)
   - Địa điểm (tùy chọn)
   - Lĩnh vực (tùy chọn)

2. **Xây Dựng URL Tìm Kiếm**
   - Sử dụng TopCV API/search
   - Áp dụng các bộ lọc

3. **Khởi Chạy Selenium Browser**
   - Undetected-chromedriver
   - Stealth options
   - Random user agent

4. **Trích Xuất Dữ Liệu**
   - Phân tích HTML với BeautifulSoup
   - Trích xuất 5 bài đăng
   - Lưu JSON đầu tiên

5. **Phân Tích Chi Tiết**
   - Lặp qua từng bài
   - Trích xuất toàn bộ thông tin
   - Định dạng tiếng Việt

6. **Xuất Báo Cáo**
   - JSON với metadata
   - Individual TXT reports
   - Combined summary report

---

## Ví Dụ Sử Dụng

### Ví Dụ 1: Tìm Kiếm Backend Developer

```bash
python enhanced_job_collector.py
# Nhập: Backend Developer
# Nhập: Senior (optional)
# Nhập: Ho Chi Minh (optional)
# Nhập: (để trống)
```

**Kết quả:**
- `collected_jobs_20250715_214844.json` (Dữ liệu thô)
- `job_analysis_1_20250715_214844.txt` (Báo cáo bài 1)
- ...
- `combined_analysis_20250715_214844.txt` (Tóm tắt tất cả)

### Ví Dụ 2: Scrape LinkedIn với Filters

```bash
python crawl_data/crawl-linkedin-jobs/scripts/scrape_linkedin.py
# Tự động scrape jobs từ LinkedIn
# Output: jobs_<timestamp>.csv/json/xlsx
```

### Ví Dụ 3: Phân Tích Batch Multiple Sites

```bash
# Tạo script combined_scrape.py để gọi tất cả crawlers
for page in {1..5}; do
    python crawl_data/crawl-vietnamwork-jobs/scripts/scrape_vietnamwork.py \
        -u "https://www.vietnamworks.com/viec-lam?q=python" \
        --start-page $page --end-page $page
done
```

---

## Troubleshooting

### Vấn Đề: ChromeDriver không tìm thấy

**Giải Pháp:**
```bash
pip install --upgrade webdriver-manager
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### Vấn Đề: CAPTCHA blocking

**Giải Pháp:**
```python
# Đã sử dụng undetected-chromedriver trong code
# Nếu vẫn bị block, chờ 30 giây rồi thử lại
```

### Vấn Đề: Connection timeout

**Giải Pháp:**
```bash
# Kiểm tra kết nối Internet
# Tăng timeout trong config
# Chạy retry script
```

### Vấn Đề: Memory error

**Giải Pháp:**
- Giảm số lượng jobs trong một lần chạy
- Làm sạch `collected_job_data/` cũ
- Tăng RAM hoặc chạy trên máy mạnh hơn

---

## Hiệu Năng & Tối Ưu Hóa

### Tốc Độ Scraping

| Nền Tảng | Tốc Độ | Jobs/Giờ | Ghi Chú |
|----------|--------|----------|--------|
| LinkedIn | Chậm | ~30-50 | JavaScript-heavy |
| VietnamWorks | Trung bình | ~100-150 | HTML tĩnh |
| ITViec | Nhanh | ~150-200 | Pagination tốt |
| CareerViet | Trung bình | ~100-150 | API-friendly |
| TopCV | Chậm | ~20-30 | Selenium required |

### Tối Ưu Hóa

1. **Sử dụng headless mode** (đã enable mặc định)
2. **Tăng workers** cho parallel scraping
3. **Cache results** để tránh duplicate scraping
4. **Batch processing** cho large datasets

---

## Đóng Góp

Chúng tôi hoan nghênh các đóng góp! Vui lòng:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

### Hướng Dẫn Đóng Góp

- Viết code sạch và có comments tiếng Anh
- Test trước khi submit
- Cập nhật `requirements.txt` nếu thêm dependencies
- Tuân thủ PEP 8 style guide

---

## Lịch Sử Phiên Bản

### v1.0.0 (Hiện Tại)
- ✅ Enhanced Job Collector cho TopCV
- ✅ LinkedIn scraper (Selenium)
- ✅ VietnamWorks scraper
- ✅ ITViec scraper
- ✅ CareerViet scraper
- ✅ Multi-format export (JSON, CSV, XLSX, TXT)
- ✅ Phân tích tiếng Việt

### Sắp Tới
- 🔄 Database integration (MongoDB/PostgreSQL)
- 🔄 REST API for data access
- 🔄 Web dashboard for visualization
- 🔄 Scheduled job scraping
- 🔄 Advanced analysis & statistics

---

## Giấy Phép

Project này được cấp phép dưới MIT License - xem [LICENSE](LICENSE) file để chi tiết.

---

## Liên Hệ & Hỗ Trợ

### Thông Tin Liên Hệ
- **Issues**: GitHub Issues tab
- **Discussions**: GitHub Discussions
- **Email**: [Your Email]

### Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra [Troubleshooting](#troubleshooting) section
2. Search GitHub Issues
3. Tạo new issue với:
   - Mô tả chi tiết
   - Error messages/logs
   - Environment info (OS, Python version)
   - Steps to reproduce

---

## Lời Cảm Ơn

Cảm ơn các libraries và frameworks:
- **Selenium** - Browser automation
- **BeautifulSoup** - HTML parsing
- **Pandas** - Data processing
- **undetected-chromedriver** - Anti-bot bypass

---

## Nguyên Tác & Tác Giả

**Dự Án Khóa Luận Tốt Nghiệp (KLTN)** - Phân Tích Thị Trường Nhân Lực Việt Nam

---

**⭐ Nếu project hữu ích, vui lòng star repository!**

*Cập nhật lần cuối: 2025-11-16*