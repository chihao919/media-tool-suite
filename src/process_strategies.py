#!/usr/bin/env python3
"""
Processing strategies using Strategy Pattern
"""

from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import os
from typing import Dict, List, Optional, Tuple
from app_constants import AppConstants


class ProcessStrategy(ABC):
    """Base strategy for media processing"""

    @abstractmethod
    def execute(self, input_file: str, output_params: Dict) -> bool:
        """Execute the processing strategy"""
        pass

    def run_ffmpeg_command(self, cmd: List[str], progress_callback=None) -> Tuple[bool, str]:
        """Run ffmpeg command and return success status and output"""
        try:
            if progress_callback:
                # Run with real-time progress monitoring
                return self._run_ffmpeg_with_progress(cmd, progress_callback)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def _run_ffmpeg_with_progress(self, cmd: List[str], progress_callback) -> Tuple[bool, str]:
        """Run ffmpeg with progress monitoring"""
        import re
        import time

        try:
            # Get total duration first
            input_file = cmd[cmd.index('-i') + 1]
            duration = self._get_media_duration(input_file)

            process = subprocess.Popen(
                cmd + ['-progress', 'pipe:1'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )

            current_time = 0
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break

                if output.startswith('out_time_ms='):
                    try:
                        time_ms = int(output.split('=')[1].strip())
                        current_time = time_ms / 1000000  # Convert to seconds
                        if duration > 0:
                            progress = min(100, (current_time / duration) * 100)
                            progress_callback(progress)
                    except (ValueError, IndexError):
                        pass  # Ignore parsing errors

            # Read stderr for error reporting
            stderr_output = process.stderr.read()
            process.wait()

            if process.returncode == 0:
                return True, ""
            else:
                return False, stderr_output

        except Exception as e:
            return False, str(e)

    def _get_media_duration(self, file_path: str) -> float:
        """Get media duration in seconds"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return 0.0


class ConvertStrategy(ProcessStrategy):
    """Strategy for converting media files"""

    def __init__(self, target_format: str, options: Dict):
        """Initialize with target format and conversion options"""
        self.target_format = target_format.lower()
        self.options = options

    def execute(self, input_file: str, output_params: Dict) -> bool:
        """Execute conversion"""
        output_file = output_params.get('output_file')
        if not output_file:
            # Generate output filename if not provided
            output_file = self._generate_output_filename(input_file, output_params)

        cmd = self._build_convert_command(input_file, output_file)
        progress_callback = output_params.get('progress_callback')
        success, _ = self.run_ffmpeg_command(cmd, progress_callback)
        return success

    def _generate_output_filename(self, input_file: str, output_params: Dict) -> str:
        """Generate output filename based on settings"""
        input_path = Path(input_file)
        output_dir = output_params.get('output_dir', input_path.parent)
        naming_style = output_params.get('naming_style', 'original')

        if naming_style == 'suffix':
            base_name = f"{input_path.stem}_converted"
        else:
            base_name = input_path.stem

        output_file = os.path.join(output_dir, f"{base_name}.{self.target_format}")
        return output_file

    def _build_convert_command(self, input_file: str, output_file: str) -> List[str]:
        """Build FFmpeg command for conversion"""
        cmd = ['ffmpeg', '-i', input_file, '-y']

        # Get codec for target format
        codec = AppConstants.get_codec_for_format(self.target_format)

        # Audio formats
        if self.target_format in ['mp3', 'aac', 'ogg', 'm4a']:
            cmd.extend(['-acodec', codec])
            if 'bitrate' in self.options:
                cmd.extend(['-b:a', self.options['bitrate']])
            if 'sample_rate' in self.options:
                cmd.extend(['-ar', self.options['sample_rate']])

        elif self.target_format == 'wav':
            cmd.extend(['-acodec', codec])
            if 'sample_rate' in self.options:
                cmd.extend(['-ar', self.options['sample_rate']])

        elif self.target_format == 'flac':
            cmd.extend(['-acodec', codec])

        # Video formats
        elif self.target_format in ['mp4', 'avi', 'mkv', 'mov', 'webm']:
            cmd.extend(['-vcodec', codec])

            # Add preset for libx264/libx265 only
            if codec == 'libx264':
                cmd.extend(['-preset', 'faster'])  # Balance between speed and quality
                cmd.extend(['-crf', '23'])  # Constant rate factor for good quality
            elif codec == 'libx265':
                cmd.extend(['-preset', 'faster'])
                cmd.extend(['-crf', '28'])

            # Set video bitrate if specified
            if 'video_bitrate' in self.options:
                cmd.extend(['-b:v', self.options['video_bitrate']])

            # Set audio parameters
            if 'audio_bitrate' in self.options:
                cmd.extend(['-acodec', 'aac', '-b:a', self.options['audio_bitrate']])
            else:
                cmd.extend(['-acodec', 'copy'])

            # Add threading for better performance
            cmd.extend(['-threads', '0'])  # Use all available CPU threads

        # Add normalization if requested
        if self.options.get('normalize', False):
            cmd.extend(['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11'])

        cmd.append(output_file)
        return cmd


class SplitStrategy(ProcessStrategy):
    """Strategy for splitting media files"""

    def __init__(self, split_mode: str, split_params: Dict):
        """Initialize with split mode and parameters"""
        self.split_mode = split_mode
        self.split_params = split_params

    def execute(self, input_file: str, output_params: Dict) -> bool:
        """Execute splitting based on mode"""
        if self.split_mode == "duration":
            return self._split_by_duration(input_file, output_params)
        elif self.split_mode == "size":
            return self._split_by_size(input_file, output_params)
        elif self.split_mode == "parts":
            return self._split_by_parts(input_file, output_params)
        return False

    def _split_by_duration(self, input_file: str, output_params: Dict) -> bool:
        """Split file by duration"""
        total_duration = self._get_media_duration(input_file)
        if total_duration <= 0:
            return False

        part_duration = float(self.split_params.get('duration', 300))
        num_parts = int(total_duration / part_duration)
        if total_duration % part_duration > 0:
            num_parts += 1

        if num_parts <= 1:
            return True  # No need to split

        return self._perform_split(input_file, output_params, num_parts, part_duration, total_duration)

    def _split_by_size(self, input_file: str, output_params: Dict) -> bool:
        """Split file by target size"""
        file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
        max_size_mb = float(self.split_params.get('size', 100))

        # Debug logging
        print(f"DEBUG: File size splitting - {os.path.basename(input_file)}")
        print(f"DEBUG: File size: {file_size_mb:.2f}MB")
        print(f"DEBUG: Target max size: {max_size_mb}MB")

        if file_size_mb <= max_size_mb:
            print(f"DEBUG: No split needed (file <= target)")
            return True  # No need to split

        total_duration = self._get_media_duration(input_file)
        if total_duration <= 0:
            print(f"DEBUG: Could not get media duration")
            return False

        print(f"DEBUG: Total duration: {total_duration} seconds")

        # Estimate number of parts based on file size
        num_parts = int(file_size_mb / max_size_mb)
        if file_size_mb % max_size_mb > 0:
            num_parts += 1

        part_duration = total_duration / num_parts

        print(f"DEBUG: Calculated {num_parts} parts")
        print(f"DEBUG: Each part duration: {part_duration:.2f} seconds")

        return self._perform_split(input_file, output_params, num_parts, part_duration, total_duration)

    def _split_by_parts(self, input_file: str, output_params: Dict) -> bool:
        """Split file into specified number of parts"""
        total_duration = self._get_media_duration(input_file)
        if total_duration <= 0:
            return False

        num_parts = int(self.split_params.get('parts', 2))
        if num_parts <= 1:
            return True  # No need to split

        part_duration = total_duration / num_parts

        return self._perform_split(input_file, output_params, num_parts, part_duration, total_duration)

    def _perform_split(self, input_file: str, output_params: Dict,
                       num_parts: int, part_duration: float, total_duration: float) -> bool:
        """Perform the actual split operation"""
        input_path = Path(input_file)
        output_dir = output_params.get('output_dir', input_path.parent)
        base_name = input_path.stem
        extension = input_path.suffix

        success_count = 0
        progress_callback = output_params.get('progress_callback')

        for i in range(num_parts):
            start_time = i * part_duration
            duration = min(part_duration, total_duration - start_time)

            output_name = f"{base_name}_part{i+1:02d}{extension}"
            output_path = os.path.join(output_dir, output_name)

            cmd = [
                'ffmpeg', '-i', input_file,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c', 'copy',  # Copy codecs for faster splitting
                '-y', output_path
            ]

            # Create a part-specific progress callback
            part_progress_callback = None
            if progress_callback:
                print(f"🎯 DEBUG: Creating part callback for part {i+1}/{num_parts}")
                def create_part_callback(part_index, total_parts, base_callback):
                    def part_callback(ffmpeg_progress):
                        # Calculate overall progress: part progress within total parts
                        part_weight = 100.0 / total_parts
                        overall_progress = (part_index * part_weight) + (ffmpeg_progress * part_weight / 100.0)
                        print(f"🎯 DEBUG: Part {part_index+1} FFmpeg progress: {ffmpeg_progress:.1f}% -> Overall: {overall_progress:.1f}%")
                        base_callback(overall_progress)
                    return part_callback

                part_progress_callback = create_part_callback(i, num_parts, progress_callback)
            else:
                print(f"⚠️  DEBUG: No progress callback provided for part {i+1}/{num_parts}")

            success, _ = self.run_ffmpeg_command(cmd, part_progress_callback)
            if success:
                success_count += 1

        # Remove original if requested
        if success_count == num_parts and not output_params.get('keep_original', False):
            try:
                os.remove(input_file)
            except OSError:
                pass  # Ignore removal errors

        return success_count == num_parts


class BatchProcessStrategy(ProcessStrategy):
    """Strategy for batch processing multiple files"""

    def __init__(self, strategy: ProcessStrategy):
        """Initialize with a base strategy to apply to all files"""
        self.strategy = strategy

    def execute(self, input_file: str, output_params: Dict) -> bool:
        """Execute strategy on single file (delegates to wrapped strategy)"""
        return self.strategy.execute(input_file, output_params)

    def execute_batch(self, input_files: List[str], output_params: Dict,
                     progress_callback: Optional[callable] = None) -> List[bool]:
        """Execute strategy on multiple files"""
        results = []
        total = len(input_files)

        for i, input_file in enumerate(input_files):
            result = self.execute(input_file, output_params)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total, Path(input_file).name)

        return results