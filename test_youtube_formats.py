#!/usr/bin/env python3
"""
測試yt-dlp如何獲取YouTube影片格式資訊
"""

import sys
import os
import yt_dlp
import json
from datetime import timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_get_video_formats():
    """測試獲取YouTube影片格式"""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print(f"🎯 測試URL: {test_url}")
    print("=" * 60)

    # Configure yt-dlp to extract info without downloading
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'listformats': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("📊 正在獲取影片資訊...")
            info = ydl.extract_info(test_url, download=False)

            print(f"📺 影片標題: {info.get('title', 'N/A')}")
            print(f"⏱️  影片長度: {info.get('duration', 'N/A')} 秒")

            if info.get('duration'):
                duration_str = str(timedelta(seconds=info['duration']))
                print(f"⏱️  影片長度: {duration_str}")

            print("\n🎥 可用格式:")
            print("-" * 60)

            formats = info.get('formats', [])

            # 分類格式
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
                tbr = fmt.get('tbr', 0)  # total bitrate
                vbr = fmt.get('vbr', 0)  # video bitrate
                abr = fmt.get('abr', 0)  # audio bitrate
                fps = fmt.get('fps')
                format_note = fmt.get('format_note', '')

                # Calculate file size
                actual_filesize = filesize or filesize_approx
                if not actual_filesize and tbr and info.get('duration'):
                    # Estimate file size from bitrate and duration
                    actual_filesize = int((tbr * 1000 * info['duration']) / 8)

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

            print("🎬 影片格式 (Video Only):")
            video_formats.sort(key=lambda x: x['height'] or 0, reverse=True)
            for fmt in video_formats[:10]:  # Show top 10
                size_str = f"{fmt['size_mb']:.1f}MB" if fmt['size_mb'] else "Unknown"
                print(f"  {fmt['format_id']:>3} | {fmt['quality_label']:>6} | {fmt['ext']:>4} | {size_str:>10} | {fmt['format_note']}")

            print("\n🎵 音頻格式 (Audio Only):")
            audio_formats.sort(key=lambda x: x['abr'] or 0, reverse=True)
            for fmt in audio_formats[:5]:  # Show top 5
                size_str = f"{fmt['size_mb']:.1f}MB" if fmt['size_mb'] else "Unknown"
                bitrate_str = f"{fmt['abr']}kbps" if fmt['abr'] else "Unknown"
                print(f"  {fmt['format_id']:>3} | Audio | {fmt['ext']:>4} | {size_str:>10} | {bitrate_str}")

            print("\n🎭 組合格式 (Video + Audio):")
            combined_formats.sort(key=lambda x: x['height'] or 0, reverse=True)
            for fmt in combined_formats[:10]:  # Show top 10
                size_str = f"{fmt['size_mb']:.1f}MB" if fmt['size_mb'] else "Unknown"
                print(f"  {fmt['format_id']:>3} | {fmt['quality_label']:>6} | {fmt['ext']:>4} | {size_str:>10} | {fmt['format_note']}")

            # Test best format selection
            print("\n🏆 推薦格式:")
            print("-" * 30)

            # Get best video qualities
            quality_options = []

            # Add combined formats first (easier for users)
            for fmt in combined_formats:
                if fmt['height'] and fmt['height'] >= 240:  # Min 240p
                    quality_options.append({
                        'label': f"{fmt['height']}p ({fmt['ext']})",
                        'format_id': fmt['format_id'],
                        'size_mb': fmt['size_mb'],
                        'type': 'combined'
                    })

            # Add best separate video+audio combinations
            if video_formats and audio_formats:
                best_audio = max(audio_formats, key=lambda x: x['abr'] or 0)
                for video_fmt in video_formats[:5]:  # Top 5 video qualities
                    if video_fmt['height']:
                        combined_size = (video_fmt['size_mb'] or 0) + (best_audio['size_mb'] or 0)
                        quality_options.append({
                            'label': f"{video_fmt['height']}p (Best Quality)",
                            'format_id': f"{video_fmt['format_id']}+{best_audio['format_id']}",
                            'size_mb': combined_size if combined_size > 0 else None,
                            'type': 'separate'
                        })

            # Add audio-only option
            if audio_formats:
                best_audio = max(audio_formats, key=lambda x: x['abr'] or 0)
                quality_options.append({
                    'label': "Audio Only (Best Quality)",
                    'format_id': best_audio['format_id'],
                    'size_mb': best_audio['size_mb'],
                    'type': 'audio'
                })

            # Remove duplicates and sort
            seen_heights = set()
            unique_options = []
            for option in quality_options:
                height_key = option['label'].split('p')[0] if 'p' in option['label'] else option['label']
                if height_key not in seen_heights or 'Audio' in option['label']:
                    seen_heights.add(height_key)
                    unique_options.append(option)

            unique_options.sort(key=lambda x: (
                0 if x['type'] == 'audio' else int(x['label'].split('p')[0]) if 'p' in x['label'] else 9999
            ), reverse=True)

            print("💡 建議的用戶選項:")
            for i, option in enumerate(unique_options[:8], 1):  # Top 8 options
                size_str = f"{option['size_mb']:.1f}MB" if option['size_mb'] else "Unknown"
                print(f"  {i}. {option['label']:20} | {size_str:>10} | ID: {option['format_id']}")

            return True

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 YouTube格式檢測工具")
    print("=" * 60)

    success = test_get_video_formats()

    if success:
        print("\n✅ 格式檢測完成")
        sys.exit(0)
    else:
        print("\n❌ 格式檢測失敗")
        sys.exit(1)