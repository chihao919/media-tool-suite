#!/usr/bin/env python3
"""
測試格式選擇功能
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_downloader import YouTubeDownloader

def test_format_selection():
    """測試格式選擇功能"""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print(f"🎯 測試格式選擇功能")
    print(f"📺 URL: {test_url}")
    print("=" * 60)

    downloader = YouTubeDownloader()

    try:
        print("📊 正在獲取可用格式...")
        formats = downloader.get_available_formats(test_url)

        if not formats:
            print("❌ 無法獲取格式資訊")
            return False

        print(f"✅ 找到 {len(formats)} 個格式選項:")
        print("-" * 60)

        for i, fmt in enumerate(formats, 1):
            size_str = f"{fmt['size_mb']:.1f}MB" if fmt['size_mb'] else "Unknown"
            print(f"  {i}. {fmt['label']:25} | {size_str:>10} | {fmt['format_id']} | {fmt['ext']}")

        print("\n🎯 選擇測試: 選擇第一個格式進行測試下載...")

        # Test format download (just extract info, don't actually download)
        test_format = formats[0]
        print(f"測試格式: {test_format['label']} ({test_format['size_mb']:.1f}MB)")

        return True

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 格式選擇功能測試")
    print("=" * 60)

    success = test_format_selection()

    if success:
        print("\n✅ 格式選擇功能測試成功")
        sys.exit(0)
    else:
        print("\n❌ 格式選擇功能測試失敗")
        sys.exit(1)