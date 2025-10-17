#!/usr/bin/env python3
"""
Application constants and configuration
"""

class AppConstants:
    """Application-wide constants"""

    # Application info
    APP_NAME = "檔案豪幫手"
    APP_VERSION = "2.0.0"

    # Supported audio formats
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}

    # Supported video formats (for future expansion)
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv'}

    # All supported media formats
    MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS

    # Available options for UI
    BITRATE_OPTIONS = ["128k", "192k", "256k", "320k"]
    AUDIO_FORMAT_OPTIONS = ["mp3", "wav", "flac", "aac", "ogg", "m4a"]
    VIDEO_FORMAT_OPTIONS = ["mp4", "avi", "mkv", "mov", "webm"]
    SAMPLE_RATE_OPTIONS = ["44100", "48000", "96000"]
    SPLIT_MODE_OPTIONS = ["duration", "size", "parts"]

    # Screen recording options
    RECORDING_FRAMERATE_OPTIONS = ["24", "30", "60"]
    RECORDING_QUALITY_OPTIONS = ["low", "medium", "high", "ultra"]

    # Default settings
    DEFAULT_SETTINGS = {
        'convert': {
            'format': 'mp3',
            'bitrate': '192k',
            'sample_rate': '44100',
            'normalize': False
        },
        'split': {
            'mode': 'duration',
            'duration': '300',
            'size': '100',
            'parts': '2',
            'keep_original': False
        },
        'recording': {
            'framerate': '30',
            'quality': 'medium',
            'output_location': 'desktop',  # 'desktop', 'ask', 'fixed'
            'fixed_output_dir': '',
            'video_device': '1',  # Default screen capture
            'audio_device': '0',  # Default audio device
        },
        'general': {
            'output_location': 'same',  # 'same', 'ask', 'fixed'
            'naming_style': 'original',  # 'original', 'suffix'
            'auto_clear': False,
            'fixed_output_dir': ''
        }
    }

    # FFmpeg codec mappings
    CODEC_MAP = {
        'mp3': 'libmp3lame',
        'aac': 'aac',
        'flac': 'flac',
        'wav': 'pcm_s16le',
        'ogg': 'libvorbis',
        'm4a': 'aac',
        'mp4': 'libx264',
        'avi': 'mpeg4',
        'mkv': 'libx264',
        'mov': 'libx264',
        'webm': 'libvpx'
    }

    # File size limits (in MB)
    DEFAULT_SPLIT_SIZE_MB = 100
    MIN_SPLIT_SIZE_MB = 1
    MAX_SPLIT_SIZE_MB = 4000

    # Duration limits (in seconds)
    DEFAULT_SPLIT_DURATION = 300  # 5 minutes
    MIN_SPLIT_DURATION = 10
    MAX_SPLIT_DURATION = 7200  # 2 hours

    # UI Settings
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    PADDING = 10

    @classmethod
    def get_file_filter(cls, media_type='audio'):
        """Generate file filter for file dialogs"""
        if media_type == 'audio':
            extensions = cls.AUDIO_EXTENSIONS
            label = "Audio Files"
        elif media_type == 'video':
            extensions = cls.VIDEO_EXTENSIONS
            label = "Video Files"
        elif media_type == 'all':
            extensions = cls.MEDIA_EXTENSIONS
            label = "Media Files"
        else:
            return [("All Files", "*.*")]

        ext_pattern = " ".join([f"*{ext}" for ext in sorted(extensions)])
        return [(label, ext_pattern), ("All Files", "*.*")]

    @classmethod
    def is_supported_format(cls, file_path: str, media_type='all') -> bool:
        """Check if file format is supported"""
        from pathlib import Path
        ext = Path(file_path).suffix.lower()

        if media_type == 'audio':
            return ext in cls.AUDIO_EXTENSIONS
        elif media_type == 'video':
            return ext in cls.VIDEO_EXTENSIONS
        else:
            return ext in cls.MEDIA_EXTENSIONS

    @classmethod
    def get_codec_for_format(cls, format_name: str) -> str:
        """Get FFmpeg codec for given format"""
        return cls.CODEC_MAP.get(format_name.lower(), 'copy')