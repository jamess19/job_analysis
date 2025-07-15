#!/usr/bin/env python3
"""
Enhanced Job Data Collector - Dựa trên pattern thành công ban đầu
Thu thập JD chi tiết theo format yêu cầu của user
"""

import time
import json
import random
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import re
import logging

class EnhancedJobCollector:
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
    def setup_logging(self):
        """Setup logging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"job_collection_{timestamp}.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_directories(self):
        """Setup directories"""
        self.data_dir = Path("collected_job_data")
        self.data_dir.mkdir(exist_ok=True)
        
    def get_enhanced_driver(self):
        """Create enhanced undetected Chrome driver"""
        options = uc.ChromeOptions()
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f'--user-agent={user_agent}')
        
        # Enhanced stealth options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            driver = uc.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.logger.info("✅ Chrome driver created successfully")
            return driver
        except Exception as e:
            self.logger.error(f"❌ Failed to create driver: {e}")
            return None
            
    def search_job_urls(self, position: str, level: str = "", location: str = "") -> List[str]:
        """Search for job URLs using the correct TopCV format"""
        driver = self.get_enhanced_driver()
        if not driver:
            return []
            
        all_urls = []
        
        try:
            # Search TopCV with correct URL format
            self.logger.info(f"🔍 Searching TopCV for: {position}")
            
            # Use the correct TopCV URL format as provided by user
            search_query = position.replace(" ", "-").lower()
            search_url = f"https://www.topcv.vn/tim-viec-lam-{search_query}?type_keyword=1&sba=1"
            
            self.logger.info(f"📋 Using URL: {search_url}")
                
            driver.get(search_url)
            time.sleep(random.uniform(5, 8))
            
            # Wait for page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Parse page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find job links with correct format: /viec-lam/.../.html
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                # Look for the correct job URL pattern as shown by user
                if '/viec-lam/' in href and '.html' in href and 'ta_source=JobSearchList_LinkDetail' in href:
                    if href.startswith('/'):
                        href = f"https://www.topcv.vn{href}"
                    if href not in all_urls:
                        all_urls.append(href)
                        self.logger.info(f"✅ Found job URL: {href[:100]}...")
                        
            # If no detailed URLs found, try simpler pattern
            if not all_urls:
                for link in links:
                    href = link['href']
                    if '/viec-lam/' in href and '.html' in href:
                        if href.startswith('/'):
                            href = f"https://www.topcv.vn{href}"
                        if href not in all_urls:
                            all_urls.append(href)
                            
            self.logger.info(f"✅ Found {len(all_urls)} job URLs total")
            
        except Exception as e:
            self.logger.error(f"❌ Error searching jobs: {e}")
        finally:
            if driver:
                driver.quit()
                
        return all_urls[:10]  # Return first 10 URLs
        
    def extract_detailed_job_info(self, job_url: str) -> Dict:
        """Extract detailed job information in the format user requested"""
        driver = self.get_enhanced_driver()
        if not driver:
            return {}
            
        try:
            self.logger.info(f"📋 Extracting details from: {job_url}")
            
            driver.get(job_url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            job_info = {
                'url': job_url,
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extract basic information
            job_info['title'] = self.extract_job_title(soup)
            job_info['company'] = self.extract_company_name(soup)
            job_info['location'] = self.extract_location(soup)
            job_info['salary'] = self.extract_salary(soup)
            
            # Find the main detail section
            detail_section = soup.find('div', class_='job-detail__information-detail')
            
            # Extract detailed JD sections using new methods
            job_info['job_description'] = self.extract_job_description(detail_section)
            
            requirements = self.extract_requirements(detail_section)
            job_info['must_have_requirements'] = requirements['must_have']
            job_info['nice_to_have_requirements'] = requirements['nice_to_have']
            
            job_info['benefits'] = self.extract_benefits(detail_section)
            job_info['work_location'] = self.extract_work_location(detail_section)
            job_info['work_time'] = self.extract_work_time(detail_section)
            
            return job_info
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting job details: {e}")
            return {'url': job_url, 'error': str(e)}
        finally:
            if driver:
                driver.quit()
                
    def extract_job_description(self, detail_section):
        """Extract job description from detail section"""
        if not detail_section:
            return []
            
        job_desc_items = []
        
        # Find the job description section
        desc_section = detail_section.find('div', class_='job-description__item')
        if desc_section:
            h3_tag = desc_section.find('h3')
            if h3_tag and 'mô tả công việc' in h3_tag.get_text().lower():
                content_div = desc_section.find('div', class_='job-description__item--content')
                if content_div:
                    # Extract list items
                    for li in content_div.find_all('li'):
                        text = li.get_text(strip=True)
                        if text:
                            job_desc_items.append(text)
                    
                    # If no list items, get paragraph text
                    if not job_desc_items:
                        for p in content_div.find_all('p'):
                            text = p.get_text(strip=True)
                            if text and len(text) > 20:
                                job_desc_items.append(text)
                                
                    # If still no content, get all text
                    if not job_desc_items:
                        text = content_div.get_text(separator='. ', strip=True)
                        if text:
                            # Split by sentences and take meaningful ones
                            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
                            job_desc_items.extend(sentences[:5])
        
        return job_desc_items[:10]  # Limit to 10 items
        
    def extract_requirements(self, detail_section):
        """Extract requirements and separate into must-have and nice-to-have"""
        if not detail_section:
            return {'must_have': [], 'nice_to_have': []}
            
        must_have = []
        nice_to_have = []
        
        # Find requirements section
        for desc_item in detail_section.find_all('div', class_='job-description__item'):
            h3_tag = desc_item.find('h3')
            if h3_tag and 'yêu cầu' in h3_tag.get_text().lower():
                content_div = desc_item.find('div', class_='job-description__item--content')
                if content_div:
                    current_section = 'must_have'
                    
                    # Check for section markers
                    for element in content_div.find_all(['p', 'ul', 'li']):
                        text = element.get_text(strip=True).lower()
                        
                        # Check for nice-to-have markers
                        if any(marker in text for marker in ['ưu tiên', 'nice to have', 'nice-to-have', 'plus', 'khuyến khích']):
                            current_section = 'nice_to_have'
                            continue
                            
                        # Extract list items based on current section
                        if element.name == 'li':
                            item_text = element.get_text(strip=True)
                            if item_text and len(item_text) > 5:
                                if current_section == 'nice_to_have':
                                    nice_to_have.append(item_text)
                                else:
                                    must_have.append(item_text)
                        
                        # Extract from paragraphs if they contain requirements
                        elif element.name == 'p' and any(keyword in text for keyword in ['kinh nghiệm', 'bằng cấp', 'kỹ năng', 'yêu cầu']):
                            if current_section == 'nice_to_have':
                                nice_to_have.append(element.get_text(strip=True))
                            else:
                                must_have.append(element.get_text(strip=True))
        
        return {
            'must_have': must_have[:15],  # Limit items
            'nice_to_have': nice_to_have[:10]
        }
        
    def extract_benefits(self, detail_section):
        """Extract benefits information"""
        if not detail_section:
            return []
            
        benefits = []
        
        # Find benefits section
        for desc_item in detail_section.find_all('div', class_='job-description__item'):
            h3_tag = desc_item.find('h3')
            if h3_tag and 'quyền lợi' in h3_tag.get_text().lower():
                content_div = desc_item.find('div', class_='job-description__item--content')
                if content_div:
                    # Extract list items
                    for li in content_div.find_all('li'):
                        text = li.get_text(strip=True)
                        if text:
                            benefits.append(text)
                    
                    # Extract from paragraphs if no list items
                    if not benefits:
                        for p in content_div.find_all('p'):
                            text = p.get_text(strip=True)
                            if text and len(text) > 10:
                                benefits.append(text)
        
        # Also check custom form benefits
        custom_benefits = detail_section.find_all('div', class_='custom-form-job__item')
        for item in custom_benefits:
            title_elem = item.find('h3', class_='custom-form-job__item--title')
            if title_elem and 'quyền lợi' in title_elem.get_text().lower():
                content_elem = item.find('div', class_='custom-form-job__item--content')
                if content_elem:
                    text = content_elem.get_text(strip=True)
                    if text:
                        benefits.append(text)
        
        return benefits[:15]  # Limit items
        
    def extract_work_location(self, detail_section):
        """Extract work location details"""
        if not detail_section:
            return "Không có thông tin"
            
        # Find work location section
        for desc_item in detail_section.find_all('div', class_='job-description__item'):
            h3_tag = desc_item.find('h3')
            if h3_tag and 'địa điểm' in h3_tag.get_text().lower():
                content_div = desc_item.find('div', class_='job-description__item--content')
                if content_div:
                    return content_div.get_text(strip=True)
        
        return "Không có thông tin chi tiết"
        
    def extract_work_time(self, detail_section):
        """Extract work time information"""
        if not detail_section:
            return "Không có thông tin"
            
        # Find work time section
        for desc_item in detail_section.find_all('div', class_='job-description__item'):
            h3_tag = desc_item.find('h3')
            if h3_tag and 'thời gian' in h3_tag.get_text().lower():
                content_div = desc_item.find('div', class_='job-description__item--content')
                if content_div:
                    return content_div.get_text(strip=True)
        
        return "Giờ hành chính"
                
    def extract_job_title(self, soup) -> str:
        """Extract job title"""
        selectors = [
            'h1.job-title', 'h1[class*="title"]', '.job-detail-title h1',
            'h1.title', '.job-header h1', 'h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if len(title) > 5:  # Valid title should be longer than 5 chars
                    return title
        return "Không xác định"
        
    def extract_company_name(self, soup) -> str:
        """Extract company name"""
        selectors = [
            '.company-name', '.job-company-name', '.company-title',
            'h2.company', '.company', '[class*="company"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                company = element.get_text(strip=True)
                if len(company) > 3:
                    return company
        return "Không xác định"
        
    def extract_location(self, soup) -> str:
        """Extract job location"""
        selectors = [
            '.job-location', '.location', '.address',
            '[class*="location"]', '[class*="address"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                location = element.get_text(strip=True)
                if len(location) > 2:
                    return location
        return "Không xác định"
        
    def extract_salary(self, soup) -> str:
        """Extract salary information"""
        selectors = [
            '.salary', '.job-salary', '.wage',
            '[class*="salary"]', '[class*="wage"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                salary = element.get_text(strip=True)
                if len(salary) > 3 and salary != "Thỏa thuận":
                    return salary
        return "Thỏa thuận"
        

        

        

        

        

        
    def format_job_analysis(self, job_data: Dict, job_number: int) -> str:
        """Format job analysis in the specific format requested by user"""
        if not job_data or 'error' in job_data:
            return f"==================== TIN TUYỂN DỤNG {job_number} ====================\n❌ Lỗi khi trích xuất thông tin\n\n"
        
        def format_list_items(items, default_msg="Chưa có thông tin chi tiết"):
            if not items:
                return f"• {default_msg}"
            if isinstance(items, list):
                return '\n'.join([f'• {item}' for item in items if item])
            return f"• {items}"
        
        analysis = f"""==================== TIN TUYỂN DỤNG {job_number} ====================
================================================================================
🎯 PHÂN TÍCH CHI TIẾT VỊ TRÍ TUYỂN DỤNG
================================================================================

📋 THÔNG TIN CƠ BẢN:
• Vị trí tuyển dụng: {job_data.get('title', 'Không xác định')}
• Công ty: {job_data.get('company', 'Không xác định')}
• Địa điểm: {job_data.get('location', 'Không xác định')}
• Cấp bậc: Tự động phân tích từ JD
• Ngành nghề/Lĩnh vực: Tự động phân tích từ JD

================================================================================
💼 MÔ TẢ CÔNG VIỆC CHÍNH:
{format_list_items(job_data.get('job_description', []), "Chưa có thông tin mô tả công việc chi tiết")}

================================================================================
✅ YÊU CẦU BẮT BUỘC (MUST-HAVE):
{format_list_items(job_data.get('must_have_requirements', []), "Chưa có thông tin yêu cầu bắt buộc chi tiết")}

================================================================================
⭐ YÊU CẦU ƯU TIÊN (NICE-TO-HAVE):
{format_list_items(job_data.get('nice_to_have_requirements', []), "Chưa có thông tin yêu cầu ưu tiên")}

================================================================================
🎁 QUYỀN LỢI & PHÚC LỢI:
{format_list_items(job_data.get('benefits', []), "Chưa có thông tin quyền lợi chi tiết")}

================================================================================
💰 MỨC LƯƠNG:
{job_data.get('salary', 'Thỏa thuận')}

================================================================================
🔗 NGUỒN: {job_data.get('url', 'N/A')}
⏰ Trích xuất lúc: {job_data.get('extracted_at', 'N/A')}
================================================================================
        """
        
        return analysis
        
    def collect_and_analyze_jobs(self, position: str, level: str = "", location: str = "", field: str = ""):
        """Main collection and analysis function"""
        print("🚀 ENHANCED JOB COLLECTOR - THEO FORMAT YÊU CẦU")
        print("=" * 80)
        print(f"🎯 Vị trí tuyển dụng: {position}")
        print(f"📊 Cấp bậc: {level if level else 'Tất cả'}")
        print(f"📍 Địa điểm: {location if location else 'Tất cả'}")
        print(f"🏢 Ngành nghề: {field if field else 'Tất cả'}")
        print("=" * 80)
        
        # Step 1: Search for job URLs
        job_urls = self.search_job_urls(position, level, location)
        
        if not job_urls:
            print("❌ Không tìm thấy tin tuyển dụng nào!")
            return
            
        print(f"\\n✅ Tìm thấy {len(job_urls)} tin tuyển dụng")
        
        # Step 2: Extract detailed information
        collected_jobs = []
        
        for i, url in enumerate(job_urls[:5], 1):  # Analyze first 5 jobs
            print(f"\\n📋 Đang phân tích tin {i}/{min(5, len(job_urls))}...")
            
            job_data = self.extract_detailed_job_info(url)
            
            if job_data and 'error' not in job_data:
                collected_jobs.append(job_data)
                
                # Format and display analysis
                analysis = self.format_job_analysis(job_data, i)
                print(analysis)
                
                # Save individual analysis
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.data_dir / f"job_analysis_{i}_{timestamp}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(analysis)
                    
                print(f"💾 Đã lưu phân tích vào: {filename}")
                
            time.sleep(random.uniform(3, 6))  # Delay between requests
            
        # Step 3: Save collected data (following successful pattern)
        if collected_jobs:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save raw data
            raw_data_file = self.data_dir / f"collected_jobs_{timestamp}.json"
            with open(raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(collected_jobs, f, ensure_ascii=False, indent=2)
                
            # Save combined analysis report
            combined_file = self.data_dir / f"combined_analysis_{timestamp}.txt"
            with open(combined_file, 'w', encoding='utf-8') as f:
                f.write(f"TỔNG HỢP PHÂN TÍCH VỊ TRÍ: {position}\\n")
                f.write("=" * 80 + "\\n\\n")
                
                for i, job in enumerate(collected_jobs, 1):
                    f.write(f"\\n{'='*20} TIN TUYỂN DỤNG {i} {'='*20}\\n")
                    f.write(self.format_job_analysis(job, i))
                    f.write("\\n\\n")
                    
            print(f"\\n📊 Dữ liệu thô: {raw_data_file}")
            print(f"📊 Báo cáo tổng hợp: {combined_file}")
            print(f"✅ Thu thập thành công {len(collected_jobs)} tin tuyển dụng!")
        else:
            print("❌ Không thu thập được tin tuyển dụng nào!")

def main():
    collector = EnhancedJobCollector()
    
    print("🎯 ENHANCED JOB COLLECTOR")
    print("=" * 50)
    
    # Input parameters
    position = input("📋 Nhập vị trí tuyển dụng (VD: Senior Frontend Developer): ").strip()
    level = input("📊 Nhập cấp bậc [Enter để bỏ qua]: ").strip()
    location = input("📍 Nhập địa điểm [Enter để bỏ qua]: ").strip()
    field = input("🏢 Nhập ngành nghề/lĩnh vực [Enter để bỏ qua]: ").strip()
    
    if not position:
        print("❌ Vui lòng nhập vị trí tuyển dụng!")
        return
        
    collector.collect_and_analyze_jobs(position, level, location, field)

if __name__ == "__main__":
    main()
