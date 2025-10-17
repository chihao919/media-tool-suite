#!/usr/bin/env python3
"""
YouTube Downloader Module for Media Tool Suite
Handles YouTube video downloading with multi-threading support
"""

import os
import sys
import threading
import queue
import time
import random
from pathlib import Path
from typing import Optional, Callable, Dict, List, Tuple
import yt_dlp
import concurrent.futures
from dataclasses import dataclass

@dataclass
class DownloadTask:
    """Represents a download task"""
    url: str
    output_path: str
    format: str = 'mp4'
    quality: str = 'best'
    split_duration: Optional[int] = None
    progress_callback: Optional[Callable] = None
    completion_callback: Optional[Callable] = None

class YouTubeDownloader:
    """YouTube video downloader with multi-threading support"""

    def __init__(self, max_workers: int = 3):
        """
        Initialize YouTube downloader

        Args:
            max_workers: Maximum number of concurrent downloads
        """
        self.max_workers = max_workers
        self.download_queue = queue.Queue()
        self.active_downloads = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()

    def download_video(self, url: str, output_path: str,
                      format: str = 'mp4', quality: str = 'best',
                      progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
        """
        Download a single YouTube video with advanced anti-detection

        Args:
            url: YouTube video URL
            output_path: Output directory path
            format: Output format (mp4, webm, etc.)
            quality: Video quality (best, 1080, 720, 480, etc.)
            progress_callback: Callback for progress updates

        Returns:
            Tuple of (success, output_file_path or error_message)
        """
        try:
            # Add random delay before starting download (0.5-3 seconds)
            time.sleep(random.uniform(0.5, 3.0))

            # Rotate between different realistic user agents
            user_agents = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            ]
            selected_user_agent = random.choice(user_agents)

            # Configure yt-dlp options with stable anti-detection
            ydl_opts = {
                'format': self._get_format_string(quality, format),
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [],
                'merge_output_format': 'mp4',
                'postprocessors': [],
                # Always ensure we get a playable format
                'postprocessor_args': {
                    'ffmpeg': ['-c:v', 'libx264', '-c:a', 'aac']
                },
                # Conservative download settings
                'concurrent_fragment_downloads': 1,
                'retries': 10,
                'fragment_retries': 10,
                'sleep_interval': 2,
                'max_sleep_interval': 5,
                'socket_timeout': 30,
                # Age verification bypass options
                'age_limit': 99,
                'skip_download': False,
                'extract_flat': False,
                'ignoreerrors': False,
                # Simplified extractor arguments
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                        'player_skip_unavailable_fragments': True,
                    }
                },
                # Simple but effective headers
                'http_headers': {
                    'User-Agent': selected_user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                },
            }

            # Always try to use browser cookies for better success rate
            # Try each browser and actually test if it works
            browsers_to_try = ['chrome', 'safari', 'firefox', 'edge']
            cookie_browser = None

            for browser in browsers_to_try:
                try:
                    # Set the browser cookies option
                    test_opts = {'cookiesfrombrowser': (browser,), 'quiet': True}
                    # Try to create a YoutubeDL instance to test if browser is available
                    import yt_dlp
                    with yt_dlp.YoutubeDL(test_opts) as test_ydl:
                        cookie_browser = browser
                        print(f"🍪 使用 {browser} 瀏覽器的 cookies")
                        break
                except Exception:
                    continue

            # Apply the working browser cookies to main options
            if cookie_browser:
                ydl_opts['cookiesfrombrowser'] = (cookie_browser,)

            # Add format converter if needed
            if format == 'mp4':
                ydl_opts['postprocessors'].append({
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                })

            # Add progress callback if provided
            if progress_callback:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded = d.get('downloaded_bytes', 0)
                        if total > 0:
                            progress = (downloaded / total) * 100
                            progress_callback(progress)
                    elif d['status'] == 'finished':
                        progress_callback(100)

                ydl_opts['progress_hooks'].append(progress_hook)

            # Try main configuration first
            try:
                print(f"🔄 嘗試主要配置...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'video')
                    ext = info.get('ext', format)

                    # Get the actual downloaded filename from yt-dlp
                    if 'requested_downloads' in info and info['requested_downloads']:
                        actual_filename = info['requested_downloads'][0].get('filepath')
                        if actual_filename and os.path.exists(actual_filename):
                            # Check if file is not empty
                            if os.path.getsize(actual_filename) > 0:
                                print(f"✅ 主要配置成功！檔案：{actual_filename}")
                                return True, actual_filename
                            else:
                                print(f"❌ 下載的檔案是空的：{actual_filename}")
                                return False, "下載的檔案是空的"

                    # Fallback: construct expected filename
                    expected_file = os.path.join(output_path, f"{self._sanitize_filename(title)}.{ext}")
                    if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                        print(f"✅ 主要配置成功！檔案：{expected_file}")
                        return True, expected_file
                    else:
                        print(f"❌ 找不到下載檔案或檔案是空的")
                        return False, "找不到下載檔案或檔案是空的"

            except Exception as main_error:
                error_msg = str(main_error)
                print(f"❌ 主要配置失敗: {error_msg[:100]}...")

                # Try simplified fallback configuration
                print(f"🔄 嘗試簡化配置...")
                time.sleep(random.uniform(3, 6))

                fallback_opts = {
                    'format': 'best[height<=720]/best',
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'merge_output_format': 'mp4',
                    'retries': 5,
                    'fragment_retries': 5,
                    'sleep_interval': 3,
                    'max_sleep_interval': 8,
                    'socket_timeout': 60,
                    'progress_hooks': [],
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android_creator'],
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                    },
                    'postprocessor_args': {
                        'ffmpeg': ['-c:v', 'libx264', '-c:a', 'aac']
                    },
                }

                # Also add cookies to fallback configuration
                if cookie_browser:
                    fallback_opts['cookiesfrombrowser'] = (cookie_browser,)

                # Add progress hook to fallback configuration
                if progress_callback:
                    # Track progress to prevent backwards movement
                    last_progress = [0]  # Use list to make it mutable in nested function
                    first_real_download = [True]  # Skip initial manifest downloads

                    def fallback_progress_hook(d):
                        if d['status'] == 'downloading':
                            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                            downloaded = d.get('downloaded_bytes', 0)

                            # Skip very small downloads (manifest files)
                            if total < 1024 * 100:  # Skip downloads smaller than 100KB
                                return

                            if total > 0:
                                progress = (downloaded / total) * 100

                                # Reset if this is the first real download after manifest
                                if first_real_download[0] and progress < 50:
                                    last_progress[0] = 0
                                    first_real_download[0] = False

                                # Only update if progress increases (smooth progress bar)
                                if progress > last_progress[0]:
                                    last_progress[0] = progress
                                    progress_callback(progress)
                        elif d['status'] == 'finished':
                            # Only call 100% for substantial downloads
                            if d.get('total_bytes', 0) > 1024 * 100:
                                progress_callback(100)

                    fallback_opts['progress_hooks'].append(fallback_progress_hook)

                try:
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        title = info.get('title', 'video')
                        ext = info.get('ext', format)

                        # Get the actual downloaded filename from yt-dlp
                        if 'requested_downloads' in info and info['requested_downloads']:
                            actual_filename = info['requested_downloads'][0].get('filepath')
                            if actual_filename and os.path.exists(actual_filename):
                                # Check if file is not empty
                                if os.path.getsize(actual_filename) > 0:
                                    print(f"✅ 簡化配置成功！檔案：{actual_filename}")
                                    return True, actual_filename
                                else:
                                    print(f"❌ 下載的檔案是空的：{actual_filename}")
                                    return False, "下載的檔案是空的"

                        # Fallback: construct expected filename
                        expected_file = os.path.join(output_path, f"{self._sanitize_filename(title)}.{ext}")
                        if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                            print(f"✅ 簡化配置成功！檔案：{expected_file}")
                            return True, expected_file
                        else:
                            print(f"❌ 找不到下載檔案或檔案是空的")
                            return False, "找不到下載檔案或檔案是空的"

                except Exception as fallback_error:
                    error_msg = str(fallback_error)
                    print(f"❌ 簡化配置也失敗: {error_msg[:100]}...")

                    # 檢查是否為年齡限制問題
                    if "Sign in to confirm your age" in error_msg:
                        print("🔞 偵測到年齡限制，正在開啟瀏覽器...")
                        import webbrowser
                        webbrowser.open(url)
                        print("📌 請在瀏覽器中：")
                        print("   1. 登入您的 YouTube 帳號")
                        print("   2. 觀看一次這個影片以通過年齡驗證")
                        print("   3. 然後再次嘗試下載")
                        return False, "AGE_VERIFICATION_REQUIRED|" + url

                    return False, f"所有配置都失敗了: {error_msg}"

        except Exception as e:
            error_msg = str(e)
            if "Sign in to confirm your age" in error_msg:
                # 自動開啟瀏覽器要求登入
                print("🔞 偵測到年齡限制，正在開啟瀏覽器...")
                import webbrowser
                webbrowser.open(url)
                return False, "AGE_VERIFICATION_REQUIRED|" + url  # Include URL for browser opening
            elif "403: Forbidden" in error_msg or "HTTP Error 403" in error_msg:
                return False, "BLOCKED_IP|" + url  # Special flag for IP blocking
            return False, error_msg

    def download_playlist(self, playlist_url: str, output_path: str,
                         format: str = 'mp4', quality: str = 'best',
                         progress_callback: Optional[Callable] = None) -> List[Tuple[str, bool, str]]:
        """
        Download all videos from a YouTube playlist

        Args:
            playlist_url: YouTube playlist URL
            output_path: Output directory path
            format: Output format
            quality: Video quality
            progress_callback: Callback for overall progress

        Returns:
            List of tuples (video_title, success, file_path_or_error)
        """
        results = []

        try:
            # Extract playlist info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)

                if 'entries' not in playlist_info:
                    return [("", False, "Not a valid playlist")]

                videos = playlist_info['entries']
                total_videos = len(videos)

                # Download each video with multi-threading
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = []

                    for i, video in enumerate(videos):
                        if video:
                            video_url = f"https://www.youtube.com/watch?v={video['id']}"

                            # Create per-video progress callback
                            def video_progress(progress, idx=i):
                                if progress_callback:
                                    overall_progress = (idx / total_videos * 100) + (progress / total_videos)
                                    progress_callback(overall_progress)

                            future = executor.submit(
                                self.download_video,
                                video_url, output_path, format, quality,
                                video_progress
                            )
                            futures.append((video.get('title', f'Video {i+1}'), future))

                    # Collect results
                    for title, future in futures:
                        success, result = future.result()
                        results.append((title, success, result))

        except Exception as e:
            results.append(("", False, str(e)))

        return results

    def download_and_split_extended(self, url: str, output_path: str,
                          split_mode: str, split_value: int,
                          format: str = 'mp4', quality: str = 'best',
                          progress_callback: Optional[Callable] = None) -> Tuple[bool, List[str]]:
        """
        Download a YouTube video and split it using existing split functionality

        Args:
            url: YouTube video URL
            output_path: Output directory path
            split_mode: 'duration', 'size', or 'parts'
            split_value: Value for splitting (seconds for duration, MB for size, number for parts)
            format: Output format
            quality: Video quality
            progress_callback: Callback for progress updates

        Returns:
            Tuple of (success, list_of_output_files or error_message)
        """
        # First download the video
        download_progress = lambda p: progress_callback(p * 0.7) if progress_callback else None
        success, video_file = self.download_video(url, output_path, format, quality, download_progress)

        if not success:
            return False, [video_file]  # video_file contains error message

        # Then split using existing split functionality
        try:
            from process_strategies import SplitStrategy
            from pathlib import Path

            # Prepare split parameters
            split_params = {}
            if split_mode == "duration":
                split_params['duration'] = split_value
            elif split_mode == "size":
                split_params['size'] = split_value
            else:  # parts
                split_params['parts'] = split_value

            # Create split strategy
            splitter = SplitStrategy(split_mode, split_params)

            # Execute split
            output_params = {'output_dir': output_path}
            split_success = splitter.execute(video_file, output_params)

            if progress_callback:
                progress_callback(100)

            if split_success:
                # Find the generated split files
                base_name = Path(video_file).stem
                ext = Path(video_file).suffix
                output_files = []

                # Look for split files with pattern: basename_partXX.ext
                import glob
                pattern = os.path.join(output_path, f"{base_name}_part*{ext}")
                output_files = sorted(glob.glob(pattern))

                if not output_files:
                    # No split files found, return original file
                    output_files = [video_file]

                return True, output_files
            else:
                return False, ["分割檔案失敗"]

        except Exception as e:
            return False, [str(e)]

    def download_and_split(self, url: str, output_path: str,
                          split_duration: int = 300,
                          format: str = 'mp4', quality: str = 'best',
                          progress_callback: Optional[Callable] = None) -> Tuple[bool, List[str]]:
        """
        Download a YouTube video and split it into segments (by duration)

        Args:
            url: YouTube video URL
            output_path: Output directory path
            split_duration: Duration of each segment in seconds
            format: Output format
            quality: Video quality
            progress_callback: Callback for progress updates

        Returns:
            Tuple of (success, list_of_output_files or error_message)
        """
        # Use the extended method with duration mode
        return self.download_and_split_extended(url, output_path, "duration",
                                              split_duration, format, quality, progress_callback)

    def _get_format_string(self, quality: str, format: str) -> str:
        """Get yt-dlp format string based on quality preference"""
        if quality == 'best':
            return 'bestvideo+bestaudio/best'
        elif quality == 'audio':
            return 'bestaudio/best'
        else:
            # Specific resolution with fallback
            height = quality.replace('p', '')
            return f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best'

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200]  # Limit length

    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get information about a YouTube video without downloading

        Args:
            url: YouTube video URL

        Returns:
            Dictionary with video information or None if error
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': [f"{f.get('format_note', 'Unknown')} ({f.get('ext', 'Unknown')})"
                               for f in info.get('formats', [])[:5]]
                }

        except Exception as e:
            print(f"Error getting video info: {e}")
            return None

    def get_available_formats(self, url: str) -> Optional[List[Dict]]:
        """
        Get available formats for a YouTube video with file sizes

        Args:
            url: YouTube video URL

        Returns:
            List of format dictionaries with quality options or None if error
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if not info:
                    return None

                formats = info.get('formats', [])
                duration = info.get('duration', 0)

                # Categorize and process formats
                video_formats = []
                audio_formats = []
                combined_formats = []

                for fmt in formats:
                    format_id = fmt.get('format_id', 'unknown')
                    ext = fmt.get('ext', 'unknown')
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    height = fmt.get('height')
                    width = fmt.get('width')
                    filesize = fmt.get('filesize')
                    filesize_approx = fmt.get('filesize_approx')
                    tbr = fmt.get('tbr', 0)
                    vbr = fmt.get('vbr', 0)
                    abr = fmt.get('abr', 0)
                    fps = fmt.get('fps')
                    format_note = fmt.get('format_note', '')

                    # Calculate file size
                    actual_filesize = filesize or filesize_approx
                    if not actual_filesize and tbr and duration:
                        # Estimate file size from bitrate and duration
                        actual_filesize = int((tbr * 1000 * duration) / 8)

                    size_mb = actual_filesize / (1024 * 1024) if actual_filesize else None

                    format_info = {
                        'format_id': format_id,
                        'ext': ext,
                        'vcodec': vcodec,
                        'acodec': acodec,
                        'height': height,
                        'width': width,
                        'filesize': actual_filesize,
                        'size_mb': size_mb,
                        'tbr': tbr,
                        'vbr': vbr,
                        'abr': abr,
                        'fps': fps,
                        'format_note': format_note,
                        'quality_label': f"{height}p" if height else "Audio",
                    }

                    # Categorize formats
                    if vcodec != 'none' and acodec != 'none':
                        combined_formats.append(format_info)
                    elif vcodec != 'none' and acodec == 'none':
                        video_formats.append(format_info)
                    elif vcodec == 'none' and acodec != 'none':
                        audio_formats.append(format_info)

                # Create user-friendly quality options
                quality_options = []

                # Add combined formats first (easier for users)
                combined_formats.sort(key=lambda x: x['height'] or 0, reverse=True)
                for fmt in combined_formats:
                    if fmt['height'] and fmt['height'] >= 240:  # Min 240p
                        quality_options.append({
                            'label': f"{fmt['height']}p ({fmt['ext']})",
                            'format_id': fmt['format_id'],
                            'size_mb': fmt['size_mb'],
                            'type': 'combined',
                            'ext': fmt['ext']
                        })

                # Add best separate video+audio combinations for higher quality
                if video_formats and audio_formats:
                    best_audio = max(audio_formats, key=lambda x: x['abr'] or 0)
                    video_formats.sort(key=lambda x: x['height'] or 0, reverse=True)

                    for video_fmt in video_formats[:5]:  # Top 5 video qualities
                        if video_fmt['height'] and video_fmt['height'] >= 480:  # Only for 480p and above
                            combined_size = (video_fmt['size_mb'] or 0) + (best_audio['size_mb'] or 0)
                            quality_options.append({
                                'label': f"{video_fmt['height']}p (Best Quality)",
                                'format_id': f"{video_fmt['format_id']}+{best_audio['format_id']}",
                                'size_mb': combined_size if combined_size > 0 else None,
                                'type': 'separate',
                                'ext': 'mp4'
                            })

                # Add audio-only options
                if audio_formats:
                    # Sort audio formats by quality
                    audio_formats.sort(key=lambda x: x['abr'] or 0, reverse=True)

                    # Add best audio option
                    best_audio = audio_formats[0]
                    quality_options.append({
                        'label': "Audio Only (Best Quality)",
                        'format_id': best_audio['format_id'],
                        'size_mb': best_audio['size_mb'],
                        'type': 'audio',
                        'ext': best_audio['ext']
                    })

                    # Add medium quality audio if available
                    if len(audio_formats) > 1:
                        medium_audio = audio_formats[len(audio_formats)//2]
                        if medium_audio['abr'] and medium_audio['abr'] != best_audio['abr']:
                            quality_options.append({
                                'label': f"Audio Only ({medium_audio['abr']}kbps)",
                                'format_id': medium_audio['format_id'],
                                'size_mb': medium_audio['size_mb'],
                                'type': 'audio',
                                'ext': medium_audio['ext']
                            })

                # Remove duplicates and limit to reasonable number
                seen_labels = set()
                unique_options = []
                for option in quality_options:
                    if option['label'] not in seen_labels:
                        seen_labels.add(option['label'])
                        unique_options.append(option)

                # Sort by quality (video) and type (audio last)
                unique_options.sort(key=lambda x: (
                    0 if x['type'] == 'audio' else
                    int(x['label'].split('p')[0]) if 'p' in x['label'] else 9999
                ), reverse=True)

                # Ensure audio options are included, then limit total
                audio_options = [opt for opt in unique_options if opt['type'] == 'audio']
                video_options = [opt for opt in unique_options if opt['type'] != 'audio']

                # Keep top 6 video options and all audio options
                final_options = video_options[:6] + audio_options

                return final_options[:8]  # Limit to 8 total options

        except Exception as e:
            print(f"Error getting video formats: {e}")
            return None

    def download_video_with_format(self, url: str, output_path: str,
                                  format_id: str, ext: str = 'mp4',
                                  progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
        """
        Download a YouTube video with specific format ID

        Args:
            url: YouTube video URL
            output_path: Output directory path
            format_id: Specific format ID (e.g., '137+140' for separate video+audio)
            ext: Expected output extension
            progress_callback: Callback for progress updates

        Returns:
            Tuple of (success, output_file_path or error_message)
        """
        try:
            # Add random delay before starting download
            time.sleep(random.uniform(0.5, 2.0))

            # Rotate between different realistic user agents
            user_agents = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
            ]
            selected_user_agent = random.choice(user_agents)

            # Configure yt-dlp options for specific format
            ydl_opts = {
                'format': format_id,
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [],
                'merge_output_format': ext,
                'postprocessors': [],
                'concurrent_fragment_downloads': 1,
                'retries': 10,
                'fragment_retries': 10,
                'sleep_interval': 2,
                'max_sleep_interval': 5,
                'socket_timeout': 30,
                'age_limit': 99,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                        'player_skip_unavailable_fragments': True,
                    }
                },
                'http_headers': {
                    'User-Agent': selected_user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                },
                'postprocessor_args': {
                    'ffmpeg': ['-c:v', 'libx264', '-c:a', 'aac']
                },
            }

            # Try to get browser cookies
            browsers_to_try = ['chrome', 'safari', 'firefox', 'edge']
            for browser in browsers_to_try:
                try:
                    test_opts = {'cookiesfrombrowser': (browser,), 'quiet': True}
                    with yt_dlp.YoutubeDL(test_opts) as test_ydl:
                        ydl_opts['cookiesfrombrowser'] = (browser,)
                        print(f"🍪 使用 {browser} 瀏覽器的 cookies")
                        break
                except Exception:
                    continue

            # Add progress callback if provided
            if progress_callback:
                last_progress = [0]
                first_real_download = [True]

                def format_progress_hook(d):
                    if d['status'] == 'downloading':
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded = d.get('downloaded_bytes', 0)

                        # Skip very small downloads (manifest files)
                        if total < 1024 * 100:  # Skip downloads smaller than 100KB
                            return

                        if total > 0:
                            progress = (downloaded / total) * 100

                            # Reset if this is the first real download after manifest
                            if first_real_download[0] and progress < 50:
                                last_progress[0] = 0
                                first_real_download[0] = False

                            # Only update if progress increases (smooth progress bar)
                            if progress > last_progress[0]:
                                last_progress[0] = progress
                                progress_callback(progress)
                    elif d['status'] == 'finished':
                        # Only call 100% for substantial downloads
                        if d.get('total_bytes', 0) > 1024 * 100:
                            progress_callback(100)

                ydl_opts['progress_hooks'].append(format_progress_hook)

            # Download with specific format
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'video')

                # Get the actual downloaded filename
                if 'requested_downloads' in info and info['requested_downloads']:
                    actual_filename = info['requested_downloads'][0].get('filepath')
                    if actual_filename and os.path.exists(actual_filename):
                        if os.path.getsize(actual_filename) > 0:
                            print(f"✅ 格式下載成功！檔案：{actual_filename}")
                            return True, actual_filename
                        else:
                            print(f"❌ 下載的檔案是空的：{actual_filename}")
                            return False, "下載的檔案是空的"

                # Fallback: construct expected filename
                expected_file = os.path.join(output_path, f"{self._sanitize_filename(title)}.{ext}")
                if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
                    print(f"✅ 格式下載成功！檔案：{expected_file}")
                    return True, expected_file
                else:
                    print(f"❌ 找不到下載檔案或檔案是空的")
                    return False, "找不到下載檔案或檔案是空的"

        except Exception as e:
            error_msg = str(e)
            print(f"❌ 格式下載失敗: {error_msg}")

            if "Requested format is not available" in error_msg:
                # Fallback to regular download if specific format fails
                print("🔄 指定格式不可用，回退到標準下載...")
                return self.download_video(url, output_path, ext, 'best', progress_callback)

            return False, error_msg

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)