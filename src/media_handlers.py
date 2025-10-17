#!/usr/bin/env python3
"""
Media handlers using Factory Pattern
"""

from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import json
from typing import Dict, Optional
from app_constants import AppConstants


class MediaHandler(ABC):
    """Base class for media handlers"""

    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """Check if this handler can process the file"""
        pass

    @abstractmethod
    def get_info(self, file_path: str) -> Dict:
        """Get media file information"""
        pass

    def get_duration(self, file_path: str) -> float:
        """Get media duration in seconds using ffprobe"""
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

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return Path(file_path).stat().st_size

    def get_format_info(self, file_path: str) -> Dict:
        """Get detailed format information using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return {}


class AudioHandler(MediaHandler):
    """Handler for audio files"""

    SUPPORTED_FORMATS = AppConstants.AUDIO_EXTENSIONS

    def can_handle(self, file_path: str) -> bool:
        """Check if file is a supported audio format"""
        return Path(file_path).suffix.lower() in self.SUPPORTED_FORMATS

    def get_info(self, file_path: str) -> Dict:
        """Get audio file information"""
        info = {
            'type': 'audio',
            'path': file_path,
            'name': Path(file_path).name,
            'extension': Path(file_path).suffix.lower(),
            'size_bytes': self.get_file_size(file_path),
            'size_mb': self.get_file_size(file_path) / (1024 * 1024),
            'duration': self.get_duration(file_path)
        }

        # Get detailed format info
        format_data = self.get_format_info(file_path)
        if format_data:
            # Extract audio stream info
            audio_stream = next(
                (s for s in format_data.get('streams', [])
                 if s.get('codec_type') == 'audio'),
                None
            )
            if audio_stream:
                info.update({
                    'codec': audio_stream.get('codec_name', 'unknown'),
                    'bitrate': format_data.get('format', {}).get('bit_rate', 'unknown'),
                    'sample_rate': audio_stream.get('sample_rate', 'unknown'),
                    'channels': audio_stream.get('channels', 'unknown')
                })

        return info


class VideoHandler(MediaHandler):
    """Handler for video files"""

    SUPPORTED_FORMATS = AppConstants.VIDEO_EXTENSIONS

    def can_handle(self, file_path: str) -> bool:
        """Check if file is a supported video format"""
        return Path(file_path).suffix.lower() in self.SUPPORTED_FORMATS

    def get_info(self, file_path: str) -> Dict:
        """Get video file information"""
        info = {
            'type': 'video',
            'path': file_path,
            'name': Path(file_path).name,
            'extension': Path(file_path).suffix.lower(),
            'size_bytes': self.get_file_size(file_path),
            'size_mb': self.get_file_size(file_path) / (1024 * 1024),
            'duration': self.get_duration(file_path)
        }

        # Get detailed format info
        format_data = self.get_format_info(file_path)
        if format_data:
            # Extract video stream info
            video_stream = next(
                (s for s in format_data.get('streams', [])
                 if s.get('codec_type') == 'video'),
                None
            )
            audio_stream = next(
                (s for s in format_data.get('streams', [])
                 if s.get('codec_type') == 'audio'),
                None
            )

            if video_stream:
                info.update({
                    'video_codec': video_stream.get('codec_name', 'unknown'),
                    'width': video_stream.get('width', 0),
                    'height': video_stream.get('height', 0),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1'))
                        if '/' in video_stream.get('r_frame_rate', '') else 0
                })

            if audio_stream:
                info.update({
                    'audio_codec': audio_stream.get('codec_name', 'unknown'),
                    'audio_bitrate': audio_stream.get('bit_rate', 'unknown'),
                    'sample_rate': audio_stream.get('sample_rate', 'unknown'),
                    'channels': audio_stream.get('channels', 'unknown')
                })

        return info


class MediaHandlerFactory:
    """Factory for creating media handlers based on file type"""

    def __init__(self):
        """Initialize with available handlers"""
        self._handlers = [
            AudioHandler(),
            VideoHandler(),
        ]

    def create_handler(self, file_path: str) -> Optional[MediaHandler]:
        """Create appropriate handler for the file"""
        for handler in self._handlers:
            if handler.can_handle(file_path):
                return handler
        return None

    def get_supported_formats(self, media_type: str = 'all') -> set:
        """Get all supported formats"""
        if media_type == 'audio':
            return AudioHandler.SUPPORTED_FORMATS
        elif media_type == 'video':
            return VideoHandler.SUPPORTED_FORMATS
        else:
            return AudioHandler.SUPPORTED_FORMATS | VideoHandler.SUPPORTED_FORMATS

    def is_supported(self, file_path: str) -> bool:
        """Check if file is supported by any handler"""
        return any(handler.can_handle(file_path) for handler in self._handlers)