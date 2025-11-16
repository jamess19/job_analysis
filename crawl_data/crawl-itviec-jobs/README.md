# ITViec Job Scraper

Scraper để thu thập thông tin tuyển dụng từ ITViec.com

## Cài đặt

```bash
pip install -r requirements.txt
```

## Sử dụng

```bash
cd scripts
python scrape_itviec.py --list-urls "https://itviec.com/it-jobs/backend" --start-page 1 --end-page 3 --out-prefix "../data-files/itviec_it_jobs"
```

## Tham số

- `--list-urls`: URL trang tìm kiếm việc làm
- `--start-page`: Trang bắt đầu (mặc định: 1)
- `--end-page`: Trang kết thúc (mặc định: 3)
- `--out-prefix`: Tiền tố file output (mặc định: "../data-files/itviec_it_jobs")

## Output

Script sẽ tạo ra:
- `{prefix}_combined.csv`: File CSV chứa dữ liệu
- `{prefix}_combined.xlsx`: File Excel chứa dữ liệu