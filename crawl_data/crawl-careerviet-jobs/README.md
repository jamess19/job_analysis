# CareerViet Job Crawler

Schema and flow aligned with `crawl-topcv-jobs`.

## Quick start (uv)
```powershell
cd "D:\Job Analytics\crawl_data\crawl-careerviet-jobs"
uv sync
uv run .\scripts\scrape_careerviet.py -u "https://careerviet.vn/viec-lam/cntt-phan-mem-c1-vi.html" --start-page 1 --end-page 1
```

## Quick start (Python venv)
```powershell
cd "D:\Job Analytics\crawl_data\crawl-careerviet-jobs"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install requests beautifulsoup4 lxml pandas urllib3 openpyxl
mkdir data-files 2>$null
python .\scripts\scrape_careerviet.py -u "https://careerviet.vn/viec-lam/cntt-phan-mem-c1-vi.html" --start-page 1 --end-page 1
```

## Output
- CSV: `data-files/careerviet_it_jobs_combined.csv`
- XLSX (requires `openpyxl`): `data-files/careerviet_it_jobs_combined.xlsx`

## Notes
- Paging rule: page 2 becomes `...-trang-2-vi.html`.
- Delay and retries are built-in. Increase sleeps if you see 429s.
