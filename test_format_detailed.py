#!/usr/bin/env python3
"""
詳細測試格式選擇功能
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_downloader import YouTubeDownloader

def test_detailed_formats():
    """詳細測試格式選擇功能"""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print(f"🎯 詳細測試格式選擇功能")
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
        print("-" * 80)
        print(f"{'No':<3} {'Label':<25} {'Size':<10} {'Type':<10} {'Format ID':<15} {'Ext'}")
        print("-" * 80)

        for i, fmt in enumerate(formats, 1):
            size_str = f"{fmt['size_mb']:.1f}MB" if fmt['size_mb'] else "Unknown"
            print(f"{i:<3} {fmt['label']:<25} {size_str:<10} {fmt['type']:<10} {fmt['format_id']:<15} {fmt['ext']}")

        # Check for audio formats specifically
        audio_formats = [f for f in formats if f['type'] == 'audio']
        print(f"\n🎵 音頻格式數量: {len(audio_formats)}")

        if not audio_formats:
            print("⚠️ 沒有找到音頻格式，讓我們檢查原始格式...")

            # Get raw format info for debugging
            import yt_dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(test_url, download=False)
                raw_formats = info.get('formats', [])

                audio_only_formats = []
                for fmt in raw_formats:
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    if vcodec == 'none' and acodec != 'none':
                        audio_only_formats.append({
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'abr': fmt.get('abr'),
                            'filesize': fmt.get('filesize'),
                            'acodec': acodec
                        })

                print(f"🔍 原始音頻格式數量: {len(audio_only_formats)}")
                for i, afmt in enumerate(audio_only_formats[:5], 1):
                    filesize = afmt['filesize'] or 0
                    size_mb = filesize / (1024 * 1024) if filesize else 0
                    print(f"  {i}. ID: {afmt['format_id']} | {afmt['ext']} | {afmt['abr']}kbps | {size_mb:.1f}MB")

        return True

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 詳細格式選擇功能測試")
    print("=" * 60)

    success = test_detailed_formats()

    if success:
        print("\n✅ 詳細格式選擇功能測試完成")
        sys.exit(0)
    else:
        print("\n❌ 詳細格式選擇功能測試失敗")
        sys.exit(1)