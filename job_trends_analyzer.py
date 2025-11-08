#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Trends Analyzer cho Job Market Analysis
Thu thập dữ liệu xu hướng tìm kiếm theo lĩnh vực và xuất CSV

Version 2.0 - Cải thiện xử lý Rate Limiting
"""

import pandas as pd
from pytrends.request import TrendReq
import time
from datetime import datetime
import os
import random

class JobTrendsAnalyzer:
    """Phân tích xu hướng công việc từ Google Trends"""
    
    def __init__(self, geo='VN', timezone=420):
        """
        Khởi tạo analyzer
        
        Args:
            geo: Khu vực địa lý (VN = Việt Nam)
            timezone: Múi giờ (420 = UTC+7 cho Việt Nam)
        """
        print("🔧 Đang khởi tạo Google Trends Analyzer...")
        self.pytrends = TrendReq(hl='vi-VN', tz=timezone, timeout=(10, 25))
        self.geo = geo
        
        # Tạo thư mục output
        self.output_dir = "trends_output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Session ID để track files của lần chạy này
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_files = []
        
        # Định nghĩa keywords theo nhóm (5 keywords/group - giới hạn của Google Trends)
        self.keyword_groups = {
            'Software_Development': [
                'Python Developer', 
                'Java Developer', 
                'JavaScript Developer', 
                'React Developer', 
                'NodeJS Developer'
            ],
            'Data_Science_AI': [
                'Data Scientist', 
                'Data Analyst', 
                'Machine Learning', 
                'AI Engineer', 
                'Big Data'
            ],
            'DevOps_Backend': [
                'DevOps Engineer', 
                'Cloud Engineer', 
                'Backend Developer', 
                'Frontend Developer', 
                'Full Stack Developer'
            ],
            'Mobile_QA': [
                'Mobile Developer', 
                'Android Developer', 
                'iOS Developer', 
                'QA Engineer', 
                'Software Tester'
            ]
        }
        
        # Định nghĩa categories (lĩnh vực)
        self.categories = {
            'All_Categories': 0,           # Tất cả danh mục
            'IT_Internet': 13,             # Công nghệ IT & Internet
            'Jobs_Education': 533          # Việc làm & Giáo dục
        }
        
        print(f"✅ Khởi tạo thành công!")
        print(f"📍 Khu vực: {self.geo}")
        print(f"📊 Số nhóm keywords: {len(self.keyword_groups)}")
        print(f"🏷️  Số categories: {len(self.categories)}")
        print(f"🆔 Session ID: {self.session_id}")
        
    def fetch_trends_data(self, keywords, category_id, timeframe='today 12-m', max_retries=3):
        """
        Lấy dữ liệu trends cho một nhóm keywords và category với retry logic
        
        Args:
            keywords: List các từ khóa (max 5)
            category_id: ID của category
            timeframe: Khung thời gian (mặc định 12 tháng)
            max_retries: Số lần retry tối đa
            
        Returns:
            DataFrame với dữ liệu trends hoặc None nếu lỗi
        """
        for attempt in range(max_retries):
            try:
                # Build payload
                self.pytrends.build_payload(
                    kw_list=keywords,
                    cat=category_id,
                    timeframe=timeframe,
                    geo=self.geo,
                    gprop=''  # Web search
                )
                
                # Lấy dữ liệu interest over time
                df = self.pytrends.interest_over_time()
                
                if df is not None and not df.empty:
                    # Xóa cột 'isPartial' nếu có
                    if 'isPartial' in df.columns:
                        df = df.drop(columns=['isPartial'])
                    return df
                else:
                    return None
                    
            except Exception as e:
                error_msg = str(e)
                
                # Kiểm tra nếu là 429 error
                if '429' in error_msg:
                    if attempt < max_retries - 1:
                        # Exponential backoff: 30s, 60s, 120s...
                        wait_time = 30 * (2 ** attempt) + random.randint(0, 10)
                        print(f"\n   ⚠️  Rate limit (429) - Attempt {attempt + 1}/{max_retries}")
                        print(f"   ⏳ Chờ {wait_time}s trước khi thử lại...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"\n   ❌ Rate limit (429) - Đã thử {max_retries} lần, bỏ qua request này")
                        return None
                else:
                    print(f"\n   ⚠️  Lỗi: {error_msg}")
                    if attempt < max_retries - 1:
                        wait_time = 10 + random.randint(0, 5)
                        print(f"   ⏳ Chờ {wait_time}s và thử lại...")
                        time.sleep(wait_time)
                        continue
                    return None
        
        return None
    
    def export_to_csv(self, df, filename):
        """
        Xuất DataFrame ra file CSV
        
        Args:
            df: DataFrame cần xuất
            filename: Tên file (không cần đuôi .csv)
        """
        if df is None or df.empty:
            print(f"   ⚠️  Không có dữ liệu để xuất cho {filename}")
            return
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        df.to_csv(filepath, encoding='utf-8-sig')
        
        # Track file của session này
        self.session_files.append(filepath)
        
        print(f"   ✅ Đã xuất: {filepath} ({len(df)} records, {len(df.columns)} keywords)")
    
    def analyze_all(self, timeframe='today 12-m', base_delay=15):
        """
        Phân tích tất cả các tổ hợp keywords và categories
        
        Args:
            timeframe: Khung thời gian
            base_delay: Thời gian chờ cơ bản giữa các requests (giây)
        """
        print("\n" + "="*80)
        print(f"🚀 BẮT ĐẦU PHÂN TÍCH GOOGLE TRENDS")
        print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 Khung thời gian: {timeframe}")
        print(f"⏳ Base delay: {base_delay}s (có random thêm 0-5s)")
        print(f"🆔 Session: {self.session_id}")
        print("="*80)
        
        total_requests = len(self.keyword_groups) * len(self.categories)
        current_request = 0
        successful_requests = 0
        
        # Lặp qua từng category
        for cat_name, cat_id in self.categories.items():
            print(f"\n📂 CATEGORY: {cat_name} (ID: {cat_id})")
            print("-" * 80)
            
            # Lặp qua từng nhóm keywords
            for group_name, keywords in self.keyword_groups.items():
                current_request += 1
                
                print(f"\n[{current_request}/{total_requests}] 🔍 Nhóm: {group_name}")
                print(f"   Keywords: {', '.join(keywords)}")
                print(f"   Đang lấy dữ liệu...", end=' ')
                
                # Lấy dữ liệu với retry logic
                df = self.fetch_trends_data(keywords, cat_id, timeframe, max_retries=3)
                
                if df is not None and not df.empty:
                    # Tạo tên file với session ID
                    filename = f"{cat_name}_{group_name}_{self.session_id}"
                    
                    # Xuất CSV
                    self.export_to_csv(df, filename)
                    successful_requests += 1
                    
                    # Hiển thị thống kê ngắn gọn
                    print(f"   📊 Thống kê:")
                    for col in df.columns:
                        mean_val = df[col].mean()
                        max_val = df[col].max()
                        print(f"      • {col:30s}: Mean={mean_val:6.2f}, Max={max_val:6.2f}")
                else:
                    print(f"   ❌ Không có dữ liệu")
                
                # Delay để tránh rate limit (trừ request cuối cùng)
                if current_request < total_requests:
                    # Random delay để tránh pattern detection
                    actual_delay = base_delay + random.randint(0, 5)
                    print(f"   ⏸️  Chờ {actual_delay}s trước request tiếp theo...")
                    time.sleep(actual_delay)
        
        print("\n" + "="*80)
        print("✅ HOÀN THÀNH TẤT CẢ PHÂN TÍCH!")
        print("="*80)
        print(f"📁 Files được lưu trong: {self.output_dir}/")
        print(f"📊 Tổng số requests: {current_request}")
        print(f"✅ Thành công: {successful_requests}")
        print(f"❌ Thất bại: {current_request - successful_requests}")
        print(f"⏰ Kết thúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Tạo file summary CHỈ từ files của session này
        if successful_requests > 0:
            self.create_summary()
        else:
            print("\n⚠️  Không có dữ liệu nào được thu thập, bỏ qua tạo summary")
    
    def create_summary(self):
        """Tạo file summary CHỈ từ files của session hiện tại"""
        print("\n📝 Đang tạo file summary từ session hiện tại...")
        
        if not self.session_files:
            print("⚠️  Không có files nào trong session này")
            return
        
        print(f"📄 Xử lý {len(self.session_files)} files từ session {self.session_id}")
        
        summary_data = []
        
        for filepath in self.session_files:
            try:
                csv_file = os.path.basename(filepath)
                df = pd.read_csv(filepath, index_col=0, parse_dates=True)
                
                # Parse filename để lấy thông tin
                parts = csv_file.replace('.csv', '').split('_')
                category = parts[0] if len(parts) > 0 else 'Unknown'
                group = parts[1] if len(parts) > 1 else 'Unknown'
                
                # Tính toán statistics cho mỗi keyword
                for col in df.columns:
                    stats = {
                        'Category': category,
                        'Group': group,
                        'Keyword': col,
                        'Mean': round(df[col].mean(), 2),
                        'Median': round(df[col].median(), 2),
                        'Max': round(df[col].max(), 2),
                        'Min': round(df[col].min(), 2),
                        'Std': round(df[col].std(), 2),
                        'Latest_Value': round(df[col].iloc[-1], 2) if len(df) > 0 else 0,
                        'First_Value': round(df[col].iloc[0], 2) if len(df) > 0 else 0,
                        'Trend': 'Up' if len(df) > 1 and df[col].iloc[-1] > df[col].iloc[0] else 'Down',
                        'Change_%': round(((df[col].iloc[-1] - df[col].iloc[0]) / (df[col].iloc[0] + 1) * 100), 2) if len(df) > 0 else 0,
                        'Weeks': len(df)
                    }
                    summary_data.append(stats)
                    
                print(f"   ✅ Đã xử lý: {csv_file}")
                    
            except Exception as e:
                print(f"   ⚠️  Lỗi khi xử lý {os.path.basename(filepath)}: {e}")
                continue
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            # Sắp xếp theo Mean giảm dần
            summary_df = summary_df.sort_values('Mean', ascending=False)
            
            # Xuất summary
            summary_file = os.path.join(self.output_dir, f"SUMMARY_{self.session_id}.csv")
            summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
            
            print(f"\n✅ Summary file: {summary_file}")
            print(f"📊 Tổng số keywords: {len(summary_df)}")
            
            # Hiển thị top 10
            print("\n🏆 TOP 10 KEYWORDS (theo Mean) - SESSION NÀY:")
            print("-" * 80)
            if len(summary_df) > 0:
                top10 = summary_df.head(10)
                for idx, row in top10.iterrows():
                    trend_icon = "📈" if row['Trend'] == 'Up' else "📉"
                    print(f"{trend_icon} {row['Keyword']:30s} | {row['Category']:15s} | Mean: {row['Mean']:6.2f} | Change: {row['Change_%']:+6.2f}%")
            
            # Phân tích thêm
            print("\n📊 PHÂN TÍCH THÊM:")
            print(f"   • Keywords trending UP: {len(summary_df[summary_df['Trend'] == 'Up'])}")
            print(f"   • Keywords trending DOWN: {len(summary_df[summary_df['Trend'] == 'Down'])}")
            print(f"   • Mean score trung bình: {summary_df['Mean'].mean():.2f}")
            print(f"   • Keyword hot nhất: {summary_df.iloc[0]['Keyword']} (Mean: {summary_df.iloc[0]['Mean']:.2f})")
        else:
            print("⚠️  Không có dữ liệu để tạo summary")
    
    def clean_old_files(self):
        """Xóa các files cũ trong thư mục output"""
        csv_files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
        
        if not csv_files:
            print("✅ Thư mục output đã sạch")
            return
        
        print(f"\n🗑️  Tìm thấy {len(csv_files)} files cũ trong {self.output_dir}/")
        print("   Bạn có muốn xóa các files cũ không? (y/n): ", end='')
        
        try:
            choice = input().strip().lower()
            if choice == 'y':
                for f in csv_files:
                    filepath = os.path.join(self.output_dir, f)
                    os.remove(filepath)
                    print(f"   🗑️  Đã xóa: {f}")
                print(f"✅ Đã xóa {len(csv_files)} files")
            else:
                print("⏭️  Giữ nguyên files cũ")
        except:
            # Non-interactive mode
            print("⏭️  Giữ nguyên files cũ (auto)")


def main():
    """Hàm main để chạy analyzer"""
    
    print("="*80)
    print("🎯 GOOGLE TRENDS ANALYZER v2.0 - JOB MARKET ANALYSIS")
    print("="*80)
    print("\n📋 Cấu hình:")
    print("   • Khu vực: Việt Nam (VN)")
    print("   • Timeframe: 12 tháng gần nhất")
    print("   • Tổng keywords: 20 (chia thành 4 nhóm)")
    print("   • Categories: 3 (All, IT/Internet, Jobs/Education)")
    print("   • Tổng số requests: 12 (4 groups × 3 categories)")
    print("   • Base delay: 15s (+ random 0-5s)")
    print("   • Retry: 3 lần với exponential backoff")
    print("\n⏱️  Thời gian ước tính: ~5-10 phút (tùy vào rate limiting)")
    print("\n💡 TIP: Nếu bị nhiều 429 errors, hãy:")
    print("   - Tăng delay lên 20-30s")
    print("   - Chạy vào ban đêm (ít traffic hơn)")
    print("   - Đợi 2-3 giờ giữa các lần chạy")
    print("="*80)
    
    # Khởi tạo analyzer
    try:
        analyzer = JobTrendsAnalyzer(geo='VN', timezone=420)
        
        # Hỏi có muốn xóa files cũ không
        analyzer.clean_old_files()
        
        # Hỏi người dùng
        print("\n❓ Bạn có muốn tiếp tục? (y/n): ", end='')
        try:
            choice = input().strip().lower()
            if choice != 'y':
                print("❌ Đã hủy.")
                return
        except:
            # Nếu running non-interactive, mặc định là yes
            print("y (auto)")
        
        print("\n🚀 Bắt đầu...\n")
        
        # Chạy phân tích
        analyzer.analyze_all(timeframe='today 12-m', base_delay=15)
        
        print("\n✨ Hoàn tất! Kiểm tra thư mục 'trends_output' để xem kết quả.")
        print(f"💡 Mở file SUMMARY_{analyzer.session_id}.csv để xem tổng hợp.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã dừng bởi người dùng.")
    except Exception as e:
        print(f"\n\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
