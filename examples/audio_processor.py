#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
from audio_utils import *

class AudioProcessor:
    def __init__(self):
        self.supported_formats = {
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.aiff', '.ape'],
            'convert_to': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']
        }

    def convert_format(self, input_path, output_format='mp3', output_dir=None, bitrate='192k'):
        """Convert audio file to another format"""
        input_path = Path(input_path)

        if not input_path.exists():
            print(f"Error: File {input_path} does not exist")
            return False

        # Set output directory
        if output_dir is None:
            output_dir = input_path.parent / f"{output_format}_output"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True)

        # Generate output filename
        output_file = output_dir / f"{input_path.stem}.{output_format}"

        # Get file size
        file_size_mb = input_path.stat().st_size / (1024 * 1024)

        print(f"\nConverting: {input_path.name} -> {output_format.upper()}")
        print(f"Input size: {file_size_mb:.2f} MB")
        print(f"Bitrate: {bitrate}")

        # Set codec based on format
        codec_map = {
            'mp3': 'libmp3lame',
            'aac': 'aac',
            'ogg': 'libvorbis',
            'flac': 'flac',
            'wav': 'pcm_s16le',
            'm4a': 'aac'
        }

        codec = codec_map.get(output_format, 'copy')

        # Build ffmpeg command
        cmd = ['ffmpeg', '-i', str(input_path)]

        if output_format == 'wav':
            # WAV doesn't use bitrate, use PCM
            cmd.extend([
                '-acodec', codec,
                '-ar', '44100',
                '-ac', '2',
                '-y',
                str(output_file)
            ])
        elif output_format == 'flac':
            # FLAC is lossless
            cmd.extend([
                '-acodec', codec,
                '-ar', '44100',
                '-y',
                str(output_file)
            ])
        else:
            # Lossy formats with bitrate
            cmd.extend([
                '-acodec', codec,
                '-b:a', bitrate,
                '-ar', '44100',
                '-y',
                str(output_file)
            ])

        try:
            print("Converting...", end="", flush=True)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                output_size_mb = output_file.stat().st_size / (1024 * 1024)
                if file_size_mb > 0:
                    compression_ratio = (1 - output_size_mb / file_size_mb) * 100
                    print(f"\r✓ Converted successfully")
                    print(f"  Output size: {output_size_mb:.2f} MB (size change: {compression_ratio:+.1f}%)")
                else:
                    print(f"\r✓ Converted successfully")
                    print(f"  Output size: {output_size_mb:.2f} MB")
                return True
            else:
                raise subprocess.CalledProcessError(process.returncode, cmd)
        except subprocess.CalledProcessError as e:
            print(f"\r❌ Error converting file: {e}")
            return False
        except Exception as e:
            print(f"\r❌ Unexpected error: {e}")
            return False

    def batch_convert(self, input_dir, output_format='mp3', output_dir=None, bitrate='192k', input_format=None):
        """Convert all audio files in a directory to specified format"""
        input_dir = Path(input_dir)

        if not input_dir.exists():
            print(f"Error: Directory {input_dir} does not exist")
            return

        # Find audio files
        audio_files = []

        if input_format:
            # Convert specific format only
            extensions = [f'.{input_format}', f'.{input_format.upper()}']
            for ext in extensions:
                audio_files.extend(input_dir.glob(f"*{ext}"))
        else:
            # Convert all supported formats
            for ext in self.supported_formats['audio']:
                audio_files.extend(input_dir.glob(f"*{ext}"))
                audio_files.extend(input_dir.glob(f"*{ext.upper()}"))

        # Filter out files that are already in target format
        audio_files = [f for f in audio_files if f.suffix.lower() != f'.{output_format}']

        if not audio_files:
            print(f"No audio files to convert in {input_dir}")
            return

        print(f"\nFound {len(audio_files)} audio file(s) to convert")
        print(f"Target format: {output_format.upper()}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # Convert all files
        successful = 0
        failed = []

        for idx, audio_file in enumerate(audio_files, 1):
            print(f"\n[{idx}/{len(audio_files)}]", end=" ")
            if self.convert_format(audio_file, output_format, output_dir, bitrate):
                successful += 1
            else:
                failed.append(audio_file.name)

        # Print summary
        print("\n" + "="*60)
        print(f"\n✅ Batch conversion complete!")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Successfully converted: {successful}/{len(audio_files)} files")

        if failed:
            print(f"\n⚠️ Failed to convert {len(failed)} file(s):")
            for filename in failed:
                print(f"  - {filename}")

        if output_dir is None:
            output_dir = input_dir / f"{output_format}_output"
        print(f"\n📁 Output files are saved in: {output_dir}")

    def normalize_batch(self, input_dir, output_dir=None, target_lufs=-16):
        """Normalize loudness of all audio files in directory"""
        input_dir = Path(input_dir)

        if not input_dir.exists():
            print(f"Error: Directory {input_dir} does not exist")
            return

        # Find audio files
        audio_files = []
        for ext in self.supported_formats['audio']:
            audio_files.extend(input_dir.glob(f"*{ext}"))
            audio_files.extend(input_dir.glob(f"*{ext.upper()}"))

        if not audio_files:
            print(f"No audio files found in {input_dir}")
            return

        if output_dir is None:
            output_dir = input_dir / "normalized_output"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True)

        print(f"\nNormalizing {len(audio_files)} audio file(s)")
        print(f"Target LUFS: {target_lufs}")
        print("="*60)

        successful = 0
        failed = []

        for idx, audio_file in enumerate(audio_files, 1):
            output_file = output_dir / audio_file.name
            print(f"\n[{idx}/{len(audio_files)}] Normalizing: {audio_file.name}")

            if normalize_audio(audio_file, output_file, target_lufs):
                successful += 1
                print(f"  ✓ Normalized successfully")
            else:
                failed.append(audio_file.name)
                print(f"  ❌ Failed to normalize")

        print("\n" + "="*60)
        print(f"\n✅ Normalization complete!")
        print(f"Successfully normalized: {successful}/{len(audio_files)} files")

        if failed:
            print(f"\n⚠️ Failed to normalize {len(failed)} file(s):")
            for filename in failed:
                print(f"  - {filename}")

        print(f"\n📁 Normalized files are saved in: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Audio Processing Tool - Convert, Split, and Normalize Audio Files')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert audio format')
    convert_parser.add_argument('input', help='Input file or directory')
    convert_parser.add_argument('-f', '--format', default='mp3',
                                choices=['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
                                help='Output format (default: mp3)')
    convert_parser.add_argument('-o', '--output', help='Output directory')
    convert_parser.add_argument('-b', '--bitrate', default='192k',
                                help='Audio bitrate (default: 192k)')
    convert_parser.add_argument('--from', dest='from_format',
                                help='Only convert files with this format')

    # Normalize command
    normalize_parser = subparsers.add_parser('normalize', help='Normalize audio loudness')
    normalize_parser.add_argument('input', help='Input directory')
    normalize_parser.add_argument('-o', '--output', help='Output directory')
    normalize_parser.add_argument('-l', '--lufs', type=float, default=-16,
                                   help='Target LUFS (default: -16)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Check if ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nError: ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)

    processor = AudioProcessor()

    if args.command == 'convert':
        input_path = Path(args.input)
        if input_path.is_file():
            processor.convert_format(input_path, args.format, args.output, args.bitrate)
        elif input_path.is_dir():
            processor.batch_convert(input_path, args.format, args.output, args.bitrate, args.from_format)
        else:
            print(f"Error: {input_path} is not a valid file or directory")
            sys.exit(1)

    elif args.command == 'normalize':
        processor.normalize_batch(args.input, args.output, args.lufs)

if __name__ == "__main__":
    main()