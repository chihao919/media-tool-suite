#!/usr/bin/env python3
import os
import subprocess
import math
import sys
from pathlib import Path
from datetime import datetime

def get_media_duration(media_path):
    """Get media (video/audio) duration in seconds using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
        str(media_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        print(f"Error getting duration for {media_path}")
        return None

def split_large_part(media_path, start_time, duration, base_output_file, part_num, total_parts):
    """Split a large part into smaller sub-parts"""
    # Split into 2 sub-parts
    sub_duration = duration / 2
    base_name = base_output_file.stem.rsplit('-', 1)[0]
    extension = base_output_file.suffix

    for j in range(2):
        sub_start = start_time + (j * sub_duration)
        sub_output = base_output_file.parent / f"{base_name}-{part_num}{chr(97+j)}{extension}"

        print(f"  Creating sub-part: {sub_output.name}")

        cmd = [
            'ffmpeg', '-i', str(media_path),
            '-ss', str(sub_start),
            '-t', str(sub_duration),
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-y',
            str(sub_output)
        ]

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                output_size_mb = sub_output.stat().st_size / (1024 * 1024)
                print(f"    ✓ Sub-part created: {output_size_mb:.2f} MB")
        except Exception as e:
            print(f"    ❌ Error creating sub-part: {e}")

def split_media(media_path, target_size_mb=180, file_num=1, total_files=1, is_audio=False):
    """Split media (video/audio) into chunks of target size using fast stream copy"""
    media_path = Path(media_path)
    file_size_mb = media_path.stat().st_size / (1024 * 1024)
    media_type = "Audio" if is_audio else "Video"

    print(f"\n{'='*60}")
    print(f"[{file_num}/{total_files}] Processing {media_type}: {media_path.name}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")

    if file_size_mb <= 200:
        print(f"Skipping {media_path.name} - size is under 200MB")
        return

    # Get media duration
    duration = get_media_duration(media_path)
    if duration is None:
        print(f"Could not process {media_path.name}")
        return

    print(f"Duration: {duration:.2f} seconds")

    # Calculate number of parts needed - use smaller target to account for keyframe imprecision
    # Using 180MB as target to ensure output stays under 200MB
    # For very large files, use even smaller target
    if file_size_mb > 350:
        actual_target = 150  # Use 150MB for very large files
    else:
        actual_target = target_size_mb
    num_parts = math.ceil(file_size_mb / actual_target)
    print(f"Will split into {num_parts} parts (target: {actual_target}MB per part)")

    # Calculate duration per part
    part_duration = duration / num_parts

    # Create output directory
    output_dir = media_path.parent / "split_output"
    output_dir.mkdir(exist_ok=True)

    # Split the media
    base_name = media_path.stem
    extension = media_path.suffix

    for i in range(num_parts):
        start_time = i * part_duration
        output_file = output_dir / f"{base_name}-{i+1}{extension}"

        print(f"\n  [{i+1}/{num_parts}] Creating: {output_file.name}")
        print(f"  Start time: {start_time:.2f}s, Duration: {part_duration:.2f}s")
        sys.stdout.flush()

        # FFmpeg command to split video using stream copy (fast)
        cmd = [
            'ffmpeg', '-i', str(media_path),
            '-ss', str(start_time),
            '-t', str(part_duration),
            '-c', 'copy',  # Stream copy - no re-encoding (FAST!)
            '-avoid_negative_ts', 'make_zero',  # Handle timestamp issues
            '-y',  # Overwrite output file
            str(output_file)
        ]

        try:
            # Show progress while running ffmpeg
            print("  Processing...", end="", flush=True)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                output_size_mb = output_file.stat().st_size / (1024 * 1024)

                # Check if output file is too large
                if output_size_mb > 200:
                    print(f"\r  ⚠️  File too large ({output_size_mb:.2f} MB), re-splitting...")
                    # Delete the oversized file
                    output_file.unlink()
                    # Recursively split this part into smaller pieces
                    split_large_part(media_path, start_time, part_duration, output_file, i+1, num_parts)
                else:
                    print(f"\r  ✓ Created: {output_size_mb:.2f} MB")
            else:
                raise subprocess.CalledProcessError(process.returncode, cmd)
        except subprocess.CalledProcessError as e:
            print(f"\r  ❌ Error with stream copy, trying re-encode...")
            # Fallback to re-encoding only if stream copy fails
            if is_audio:
                # For audio files, use appropriate codecs
                cmd_reencode = [
                    'ffmpeg', '-i', str(media_path),
                    '-ss', str(start_time),
                    '-t', str(part_duration),
                    '-c:a', 'aac',  # Re-encode audio to AAC
                    '-b:a', '192k',  # Audio bitrate
                    '-y',
                    str(output_file)
                ]
            else:
                # For video files
                cmd_reencode = [
                    'ffmpeg', '-i', str(media_path),
                    '-ss', str(start_time),
                    '-t', str(part_duration),
                    '-c:v', 'libx264',  # Re-encode video
                    '-preset', 'ultrafast',  # Fastest preset
                    '-crf', '23',  # Quality setting
                    '-c:a', 'aac',  # Re-encode audio
                    '-b:a', '128k',
                    '-y',
                    str(output_file)
                ]
            try:
                print("  Re-encoding (slower)...", end="", flush=True)
                process = subprocess.Popen(cmd_reencode, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    output_size_mb = output_file.stat().st_size / (1024 * 1024)
                    print(f"\r  ✓ Created (re-encoded): {output_size_mb:.2f} MB")
                else:
                    raise subprocess.CalledProcessError(process.returncode, cmd_reencode)
            except subprocess.CalledProcessError as e2:
                print(f"\r  ❌ Failed to create part {i+1}: {e2}")

def main():
    video_dir = Path("./video")

    # Check if directory exists
    if not video_dir.exists():
        print(f"Directory {video_dir} does not exist.")
        print("\nPlease ensure the /video directory exists and contains video files.")
        print("You may need to create it with appropriate permissions:")
        print("  sudo mkdir -p /video")
        print("  sudo chmod 755 /video")
        return

    # Find all video and audio files
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg']
    audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.aiff', '.ape']

    video_files = []
    audio_files = []

    # Find video files
    for ext in video_extensions:
        video_files.extend(video_dir.glob(f"*{ext}"))
        video_files.extend(video_dir.glob(f"*{ext.upper()}"))

    # Find audio files
    for ext in audio_extensions:
        audio_files.extend(video_dir.glob(f"*{ext}"))
        audio_files.extend(video_dir.glob(f"*{ext.upper()}"))

    total_files = len(video_files) + len(audio_files)

    if not total_files:
        print(f"No media files found in {video_dir}")
        print(f"Supported video formats: {', '.join(video_extensions)}")
        print(f"Supported audio formats: {', '.join(audio_extensions)}")
        return

    print(f"\nFound {len(video_files)} video file(s) and {len(audio_files)} audio file(s)")
    print(f"Total: {total_files} media file(s)")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Check if ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nError: ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return

    # Process all media files
    processed = 0
    errors = []
    all_media = [(f, False) for f in video_files] + [(f, True) for f in audio_files]

    for idx, (media_file, is_audio) in enumerate(all_media, 1):
        try:
            split_media(media_file, target_size_mb=180, file_num=idx, total_files=total_files, is_audio=is_audio)
            processed += 1
        except Exception as e:
            error_msg = f"Error processing {media_file.name}: {e}"
            print(f"\n❌ {error_msg}")
            errors.append(error_msg)

    print("\n" + "="*60)
    print(f"\n✅ Processing complete!")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Successfully processed: {processed}/{total_files} files")

    if errors:
        print(f"\n⚠️ Errors occurred with {len(errors)} file(s):")
        for error in errors:
            print(f"  - {error}")

    if (video_dir / "split_output").exists():
        print(f"\n📁 Split media files are saved in: {video_dir}/split_output")

if __name__ == "__main__":
    main()