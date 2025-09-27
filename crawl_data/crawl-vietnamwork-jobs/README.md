# VietnamWorks Job Crawler

Schema and flow aligned with `crawl-topcv-jobs`.

## Quick start (uv)
```powershell
cd "D:\Job Analytics\crawl_data\crawl-vietnamwork-jobs"
uv sync
uv run .\scripts\scrape_vietnamwork.py -u "https://www.vietnamworks.com/viec-lam?q=backend&g=5" --start-page 1 --end-page 2 --no-company
```

## Quick start (Python venv)
```powershell
cd "D:\Job Analytics\crawl_data\crawl-vietnamwork-jobs"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # or: pip install requests beautifulsoup4 lxml pandas urllib3
mkdir data-files 2>$null
python .\scripts\scrape_vietnamwork.py -u "https://www.vietnamworks.com/viec-lam?q=backend&g=5" --start-page 1 --end-page 2 --no-company
```

## Output
- CSV: `data-files/vietnamworks_it_jobs_combined.csv`
- XLSX (install `openpyxl`): `data-files/vietnamworks_it_jobs_combined.xlsx`

## Notes
- `--no-company` to skip company pages (some require auth and return 404).
- `--no-next` to disable parsing Next.js embedded JSON if needed.
- Tune delays via code if rate-limited (429).
