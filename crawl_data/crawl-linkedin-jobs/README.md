# LinkedIn Job Crawler

This module crawls job listings from LinkedIn and extracts relevant information.

## Features

- Search for jobs by keyword and location
- Extract detailed job information including:
  - Job title and description
  - Company information
  - Salary (when available)
  - Location
  - Experience requirements
  - Job type (full-time, part-time, etc.)

## Usage

```python
from scripts.scrape_linkedin import LinkedInJobCrawler

crawler = LinkedInJobCrawler()
jobs = crawler.crawl_jobs(keyword="Software Engineer", location="Vietnam", max_jobs=100)
```

## Note

LinkedIn has strict anti-bot measures. This crawler:
- Uses realistic delays between requests
- Rotates user agents
- Implements proper session management
- Respects robots.txt and rate limits

Please use responsibly and in accordance with LinkedIn's Terms of Service.