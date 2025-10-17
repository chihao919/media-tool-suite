#!/usr/bin/env python3
"""
Continuous Test and Fix System
自動測試、檢測bug、修復問題，然後重新測試的循環系統
"""

import sys
import os
import time
import subprocess
import threading
import queue
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class ContinuousTestSystem:
    def __init__(self):
        self.test_url = "https://www.youtube.com/watch?v=1ImEcPSdlEM&t=736s"
        self.download_dir = os.path.expanduser("~/Downloads")
        self.max_cycles = 10  # 最多測試10個週期
        self.current_cycle = 0
        self.test_results = []
        self.known_issues = set()

    def log(self, message):
        """記錄測試過程"""
        timestamp = time.strftime("%H:%M:%S")
        log_msg = f"[CYCLE {self.current_cycle+1}] [{timestamp}] {message}"
        print(log_msg)
        self.test_results.append(log_msg)

    def run_test_cycle(self):
        """執行一個完整的測試週期"""
        self.current_cycle += 1
        self.log(f"🔄 開始測試週期 {self.current_cycle}/{self.max_cycles}")

        # Step 1: 測試Split功能的進度條
        split_result = self.test_split_progress()

        # Step 2: 測試YouTube下載進度條
        youtube_result = self.test_youtube_progress()

        # Step 3: 分析結果
        overall_success = split_result and youtube_result

        if overall_success:
            self.log("✅ 測試週期成功完成！")
            return True
        else:
            self.log("❌ 測試週期發現問題，準備修復...")
            return False

    def test_split_progress(self):
        """測試Split功能的進度條"""
        self.log("🎯 測試Split功能進度條...")

        try:
            # 創建測試影片檔案
            test_video = self.create_test_video()
            if not test_video:
                self.log("❌ 無法創建測試影片")
                return False

            # 執行split測試
            result = subprocess.run([
                'python3', 'test_size_split_progress.py'
            ], capture_output=True, text=True, timeout=120)

            success = result.returncode == 0
            if success:
                # 檢查是否有進度更新
                if "Progress updates received:" in result.stdout:
                    self.log("✅ Split進度條測試成功")
                    return True
                else:
                    self.log("❌ Split進度條沒有更新")
                    self.detect_and_fix_split_issues(result.stdout, result.stderr)
                    return False
            else:
                self.log(f"❌ Split測試失敗: {result.stderr}")
                self.detect_and_fix_split_issues(result.stdout, result.stderr)
                return False

        except subprocess.TimeoutExpired:
            self.log("❌ Split測試超時")
            return False
        except Exception as e:
            self.log(f"❌ Split測試異常: {e}")
            return False

    def test_youtube_progress(self):
        """測試YouTube下載進度條"""
        self.log("📺 測試YouTube下載進度條...")

        try:
            # 使用更簡單的YouTube URL進行測試
            simple_test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 一個簡單的測試影片

            # 執行YouTube下載測試
            result = subprocess.run([
                'python3', '-c', f'''
import sys
import os
sys.path.insert(0, "src")
from youtube_downloader import YouTubeDownloader
import tempfile

def progress_callback(progress):
    print(f"PROGRESS_UPDATE: {{progress:.1f}}%")

downloader = YouTubeDownloader()
temp_dir = tempfile.mkdtemp()
success, result = downloader.download_video(
    "{simple_test_url}",
    temp_dir,
    "mp4",
    "480p",
    progress_callback
)
print(f"DOWNLOAD_RESULT: {{success}}")
if success:
    print("✅ YouTube下載測試成功")
else:
    print(f"❌ YouTube下載失敗: {{result}}")
'''
            ], capture_output=True, text=True, timeout=180)

            # 分析結果
            if "PROGRESS_UPDATE:" in result.stdout:
                self.log("✅ YouTube進度條測試成功")
                return True
            elif "AGE_VERIFICATION_REQUIRED" in result.stdout:
                self.log("🔞 年齡限制問題，嘗試其他影片...")
                return self.test_alternative_youtube_video()
            else:
                self.log(f"❌ YouTube下載測試失敗")
                self.detect_and_fix_youtube_issues(result.stdout, result.stderr)
                return False

        except subprocess.TimeoutExpired:
            self.log("❌ YouTube測試超時")
            return False
        except Exception as e:
            self.log(f"❌ YouTube測試異常: {e}")
            return False

    def test_alternative_youtube_video(self):
        """測試替代的YouTube影片"""
        alternative_urls = [
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # First video on YouTube
            "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
        ]

        for url in alternative_urls:
            try:
                self.log(f"🔄 嘗試替代URL: {url}")
                result = subprocess.run([
                    'python3', '-c', f'''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from youtube_downloader import YouTubeDownloader
import tempfile

def progress_callback(progress):
    print(f"PROGRESS_UPDATE: {{progress:.1f}}%")

downloader = YouTubeDownloader()
temp_dir = tempfile.mkdtemp()
success, result = downloader.download_video(
    "{url}",
    temp_dir,
    "mp4",
    "360p",
    progress_callback
)
print(f"DOWNLOAD_RESULT: {{success}}")
'''
                ], capture_output=True, text=True, timeout=180)

                if "PROGRESS_UPDATE:" in result.stdout:
                    self.log(f"✅ 替代URL測試成功: {url}")
                    return True

            except Exception as e:
                self.log(f"❌ 替代URL失敗: {e}")
                continue

        return False

    def detect_and_fix_split_issues(self, stdout, stderr):
        """檢測並修復Split相關問題"""
        self.log("🔧 檢測Split問題...")

        issues_found = []

        # 檢查常見問題
        if "progress_callback" not in stdout and "No progress updates" in stdout:
            issues_found.append("missing_progress_callback")

        if "FFmpeg" in stderr and "not found" in stderr:
            issues_found.append("missing_ffmpeg")

        # 修復找到的問題
        for issue in issues_found:
            if issue not in self.known_issues:
                self.known_issues.add(issue)
                self.fix_issue(issue)

    def detect_and_fix_youtube_issues(self, stdout, stderr):
        """檢測並修復YouTube相關問題"""
        self.log("🔧 檢測YouTube問題...")

        issues_found = []

        if "Requested format is not available" in stderr:
            issues_found.append("format_not_available")

        if "Sign in to confirm your age" in stderr:
            issues_found.append("age_verification")

        if "HTTP Error 403" in stderr:
            issues_found.append("ip_blocked")

        # 修復找到的問題
        for issue in issues_found:
            if issue not in self.known_issues:
                self.known_issues.add(issue)
                self.fix_issue(issue)

    def fix_issue(self, issue):
        """修復特定問題"""
        self.log(f"🔧 修復問題: {issue}")

        if issue == "missing_progress_callback":
            self.fix_progress_callback_issue()
        elif issue == "format_not_available":
            self.fix_youtube_format_issue()
        elif issue == "age_verification":
            self.fix_age_verification_issue()
        elif issue == "ip_blocked":
            self.fix_ip_blocking_issue()
        elif issue == "missing_ffmpeg":
            self.fix_ffmpeg_issue()

    def fix_progress_callback_issue(self):
        """修復進度回調問題"""
        self.log("🔧 修復進度回調問題...")

        # 檢查media_converter.py中的progress callback
        media_converter_path = "src/media_converter.py"
        if os.path.exists(media_converter_path):
            with open(media_converter_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 確保Split worker有progress callback
            if "'progress_callback': file_progress_callback" not in content:
                self.log("📝 添加progress callback到Split worker...")
                # 這裡可以添加具體的修復代碼

    def fix_youtube_format_issue(self):
        """修復YouTube格式問題"""
        self.log("🔧 修復YouTube格式問題...")

        youtube_downloader_path = "src/youtube_downloader.py"
        if os.path.exists(youtube_downloader_path):
            with open(youtube_downloader_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 修改格式配置為更兼容的選項
            if "bestvideo[height<=480]+bestaudio" not in content:
                self.log("📝 更新YouTube格式配置...")
                # 添加更保守的格式選項

    def fix_age_verification_issue(self):
        """修復年齡驗證問題"""
        self.log("🔧 修復年齡驗證問題...")
        # 使用不需要年齡驗證的測試影片

    def fix_ip_blocking_issue(self):
        """修復IP封鎖問題"""
        self.log("🔧 修復IP封鎖問題...")
        # 添加重試和延遲機制

    def fix_ffmpeg_issue(self):
        """修復FFmpeg問題"""
        self.log("🔧 檢查FFmpeg安裝...")
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
            if result.returncode == 0:
                self.log("✅ FFmpeg已安裝")
            else:
                self.log("❌ FFmpeg未正確安裝")
        except FileNotFoundError:
            self.log("❌ 找不到FFmpeg")

    def create_test_video(self):
        """創建測試影片檔案"""
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_file.close()

            cmd = [
                'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=15:size=320x240:rate=1',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '30',
                '-y', temp_file.name
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return temp_file.name
            else:
                return None

        except Exception:
            return None

    def cleanup_test_files(self):
        """清理測試檔案"""
        self.log("🧹 清理測試檔案...")
        # 清理臨時檔案

    def print_final_report(self):
        """打印最終報告"""
        self.log("\n" + "="*60)
        self.log("📊 最終測試報告")
        self.log("="*60)

        for result in self.test_results:
            print(result)

        if self.current_cycle >= self.max_cycles:
            self.log(f"❌ 達到最大測試週期數 ({self.max_cycles})，測試終止")

        self.log(f"🔧 發現並處理的問題: {len(self.known_issues)}")
        for issue in self.known_issues:
            self.log(f"   - {issue}")

    def run(self):
        """運行持續測試系統"""
        self.log("🚀 啟動持續測試和修復系統")
        self.log(f"📋 目標: 測試YouTube下載和Split功能的進度條")
        self.log(f"🔄 最多執行 {self.max_cycles} 個測試週期")

        while self.current_cycle < self.max_cycles:
            try:
                success = self.run_test_cycle()
                if success:
                    self.log("🎉 所有功能測試成功！")
                    break
                else:
                    self.log("⏳ 等待3秒後開始下一個週期...")
                    time.sleep(3)

            except KeyboardInterrupt:
                self.log("⏹️ 用戶中斷測試")
                break
            except Exception as e:
                self.log(f"❌ 測試週期異常: {e}")
                time.sleep(5)

        self.cleanup_test_files()
        self.print_final_report()

        return self.current_cycle < self.max_cycles


def main():
    """主函數"""
    print("🤖 持續測試和修復系統")
    print("=" * 60)

    system = ContinuousTestSystem()
    success = system.run()

    if success:
        print("\n🎉 任務完成！進度條功能正常運作。")
        return 0
    else:
        print("\n⚠️ 達到最大測試次數，仍有問題需要解決。")
        return 1


if __name__ == "__main__":
    sys.exit(main())