#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def convert_wav_to_mp3(wav_path, output_dir=None, bitrate='192k', file_num=1, total_files=1):
    """Convert WAV file to MP3 format using ffmpeg"""
    wav_path = Path(wav_path)

    if not wav_path.exists():
        print(f"Error: File {wav_path} does not exist")
        return False

    # Set output directory - default to same directory as source file
    if output_dir is None:
        output_dir = wav_path.parent  # Same directory as source
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

    # Generate output filename
    output_file = output_dir / f"{wav_path.stem}.mp3"

    # Get file size
    file_size_mb = wav_path.stat().st_size / (1024 * 1024)

    print(f"\n[{file_num}/{total_files}] Converting: {wav_path.name}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Output: {output_file.name}")
    print(f"Bitrate: {bitrate}")

    # FFmpeg command to convert WAV to MP3
    cmd = [
        'ffmpeg', '-i', str(wav_path),
        '-acodec', 'libmp3lame',  # Use LAME encoder for MP3
        '-b:a', bitrate,           # Audio bitrate
        '-ar', '44100',            # Sample rate
        '-y',                      # Overwrite output file
        str(output_file)
    ]

    try:
        print("Converting...", end="", flush=True)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            output_size_mb = output_file.stat().st_size / (1024 * 1024)
            compression_ratio = (1 - output_size_mb / file_size_mb) * 100
            print(f"\r✓ Converted successfully")
            print(f"  Output size: {output_size_mb:.2f} MB (compressed {compression_ratio:.1f}%)")
            return True
        else:
            raise subprocess.CalledProcessError(process.returncode, cmd)
    except subprocess.CalledProcessError as e:
        print(f"\r❌ Error converting file: {e}")
        if stderr:
            print(f"FFmpeg error: {stderr.decode('utf-8', errors='ignore')[:200]}")
        return False
    except Exception as e:
        print(f"\r❌ Unexpected error: {e}")
        return False

def batch_convert_wav_to_mp3(input_dir, output_dir=None, bitrate='192k'):
    """Convert all WAV files in a directory to MP3 format"""
    input_dir = Path(input_dir)

    if not input_dir.exists():
        print(f"Error: Directory {input_dir} does not exist")
        return

    # Find all WAV files
    wav_files = list(input_dir.glob("*.wav"))
    wav_files.extend(input_dir.glob("*.WAV"))

    if not wav_files:
        print(f"No WAV files found in {input_dir}")
        return

    print(f"\nFound {len(wav_files)} WAV file(s)")
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

    # Convert all WAV files
    successful = 0
    failed = []

    for idx, wav_file in enumerate(wav_files, 1):
        if convert_wav_to_mp3(wav_file, output_dir, bitrate, idx, len(wav_files)):
            successful += 1
        else:
            failed.append(wav_file.name)

    # Print summary
    print("\n" + "="*60)
    print(f"\n✅ Conversion complete!")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Successfully converted: {successful}/{len(wav_files)} files")

    if failed:
        print(f"\n⚠️ Failed to convert {len(failed)} file(s):")
        for filename in failed:
            print(f"  - {filename}")

    if output_dir is None:
        print(f"\n📁 MP3 files are saved in their original directories")
    else:
        print(f"\n📁 MP3 files are saved in: {output_dir}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Convert WAV files to MP3 format')
    parser.add_argument('input', nargs='?', default='./video',
                        help='Input directory or WAV file path (default: ./video)')
    parser.add_argument('-o', '--output', help='Output directory (default: same as input file)')
    parser.add_argument('-b', '--bitrate', default='192k',
                        help='Audio bitrate (default: 192k, options: 128k, 192k, 256k, 320k)')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file() and input_path.suffix.lower() == '.wav':
        # Convert single file
        convert_wav_to_mp3(input_path, args.output, args.bitrate)
    elif input_path.is_dir():
        # Convert all WAV files in directory
        batch_convert_wav_to_mp3(input_path, args.output, args.bitrate)
    else:
        print(f"Error: {input_path} is not a valid WAV file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()