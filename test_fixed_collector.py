#!/usr/bin/env python3
"""
Test Fixed Enhanced Job Collector
"""

from enhanced_job_collector import EnhancedJobCollector

def main():
    print("🚀 TEST FIXED ENHANCED JOB COLLECTOR")
    print("=" * 60)
    
    collector = EnhancedJobCollector()
    
    # Test với vị trí cụ thể
    position = "Software Engineer"
    
    print(f"\n🎯 Testing: {position}")
    print("-" * 40)
    
    try:
        collector.collect_and_analyze_jobs(
            position=position,
            level="",
            location="",
            field=""
        )
        print(f"✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
