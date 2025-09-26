#!/usr/bin/env python3
import subprocess
from pathlib import Path

def get_audio_duration(audio_path):
    """Get audio duration in seconds using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
        str(audio_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        print(f"Error getting duration for {audio_path}")
        return None

def convert_audio(input_path, output_path, codec='libmp3lame', bitrate='192k', sample_rate='44100'):
    """Generic audio conversion function"""
    cmd = [
        'ffmpeg', '-i', str(input_path),
        '-acodec', codec,
        '-b:a', bitrate,
        '-ar', sample_rate,
        '-y',
        str(output_path)
    ]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return process.returncode == 0
    except Exception as e:
        print(f"Error converting audio: {e}")
        return False

def split_audio(audio_path, start_time, duration, output_path, use_copy=True):
    """Split audio file into segments"""
    if use_copy:
        # Try stream copy first (faster)
        cmd = [
            'ffmpeg', '-i', str(audio_path),
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-y',
            str(output_path)
        ]
    else:
        # Re-encode if necessary
        cmd = [
            'ffmpeg', '-i', str(audio_path),
            '-ss', str(start_time),
            '-t', str(duration),
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            str(output_path)
        ]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return process.returncode == 0
    except Exception as e:
        print(f"Error splitting audio: {e}")
        return False

def get_audio_info(audio_path):
    """Get detailed audio information"""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration,size,bit_rate:stream=codec_name,sample_rate,channels,bit_rate',
        '-of', 'json',
        str(audio_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Error getting audio info: {e}")
        return None

def normalize_audio(input_path, output_path, target_lufs=-16):
    """Normalize audio loudness using ffmpeg loudnorm filter"""
    # First pass to analyze
    analyze_cmd = [
        'ffmpeg', '-i', str(input_path),
        '-af', f'loudnorm=I={target_lufs}:print_format=json',
        '-f', 'null', '-'
    ]

    try:
        process = subprocess.Popen(analyze_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Extract loudnorm stats from stderr
        import json
        import re

        # Find JSON in stderr
        stderr_str = stderr.decode('utf-8', errors='ignore')
        json_match = re.search(r'\{[^}]+\}', stderr_str[::-1])

        if json_match:
            # Second pass with measured values
            normalize_cmd = [
                'ffmpeg', '-i', str(input_path),
                '-af', f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11',
                '-ar', '44100',
                '-y',
                str(output_path)
            ]

            process = subprocess.Popen(normalize_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            return process.returncode == 0
    except Exception as e:
        print(f"Error normalizing audio: {e}")

    # Fallback to simple normalization
    return convert_audio(input_path, output_path)