#!/usr/bin/env python3
"""
YouTube下載進度條Debug測試
"""

import sys
import os
import tempfile

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube_downloader import YouTubeDownloader


def test_youtube_progress():
    """測試YouTube下載進度回調"""
    print("🎯 測試YouTube下載進度回調...")

    progress_updates = []

    def progress_callback(progress):
        progress_updates.append(progress)
        print(f"PROGRESS_UPDATE: {progress:.1f}%")

    downloader = YouTubeDownloader()
    temp_dir = tempfile.mkdtemp()

    print(f"📁 臨時目錄: {temp_dir}")
    print("⬇️ 開始下載測試...")

    try:
        success, result = downloader.download_video(
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            temp_dir,
            'mp4',
            '360p',
            progress_callback
        )

        print(f"DOWNLOAD_RESULT: {success}")
        print(f"進度更新次數: {len(progress_updates)}")

        if progress_updates:
            print(f"進度範圍: {min(progress_updates):.1f}% - {max(progress_updates):.1f}%")
            print("✅ 進度回調正常工作")
        else:
            print("❌ 沒有收到進度更新")

        if not success:
            print(f"❌ 下載失敗: {result}")
        else:
            print(f"✅ 下載成功: {result}")

        return success and len(progress_updates) > 0

    except Exception as e:
        print(f"❌ 測試異常: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理臨時目錄
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("🤖 YouTube下載進度條Debug測試")
    print("=" * 50)

    result = test_youtube_progress()

    print("\n" + "=" * 50)
    if result:
        print("🎉 YouTube進度條測試成功！")
        sys.exit(0)
    else:
        print("❌ YouTube進度條測試失敗")
        sys.exit(1)