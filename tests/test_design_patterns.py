#!/usr/bin/env python3
"""
Test file for new design patterns implementation
"""

import os
from pathlib import Path
from media_processor import MediaProcessor, MediaProcessorBuilder
from media_handlers import MediaHandlerFactory
from app_constants import AppConstants


def test_factory_pattern():
    """Test Factory Pattern"""
    print("Testing Factory Pattern...")

    factory = MediaHandlerFactory()

    # Test audio file support
    audio_file = "test.mp3"
    if factory.is_supported(audio_file):
        print(f"✓ {audio_file} is supported")

    # Test video file support
    video_file = "test.mp4"
    if factory.is_supported(video_file):
        print(f"✓ {video_file} is supported")

    # Test unsupported file
    unsupported_file = "test.xyz"
    if not factory.is_supported(unsupported_file):
        print(f"✓ {unsupported_file} is not supported (as expected)")

    # Test supported formats
    audio_formats = factory.get_supported_formats('audio')
    print(f"✓ Supported audio formats: {audio_formats}")

    video_formats = factory.get_supported_formats('video')
    print(f"✓ Supported video formats: {video_formats}")

    print("Factory Pattern tests passed!\n")


def test_strategy_pattern():
    """Test Strategy Pattern"""
    print("Testing Strategy Pattern...")

    # Test converter builder
    converter = MediaProcessorBuilder.create_converter(
        format='mp3',
        bitrate='192k',
        sample_rate='44100'
    )
    print(f"✓ Created converter for MP3 format")

    # Test splitter builder
    splitter = MediaProcessorBuilder.create_splitter(
        mode='duration',
        duration=300
    )
    print(f"✓ Created splitter with duration mode")

    # Test batch processors
    batch_converter = MediaProcessorBuilder.create_batch_converter(
        format='flac',
        bitrate='320k'
    )
    print(f"✓ Created batch converter for FLAC format")

    print("Strategy Pattern tests passed!\n")


def test_constants():
    """Test AppConstants"""
    print("Testing AppConstants...")

    # Test default settings
    assert AppConstants.DEFAULT_SETTINGS['convert']['format'] == 'mp3'
    print(f"✓ Default convert format: {AppConstants.DEFAULT_SETTINGS['convert']['format']}")

    # Test file filter generation
    audio_filter = AppConstants.get_file_filter('audio')
    print(f"✓ Audio file filter generated: {audio_filter[0][0]}")

    # Test codec mapping
    mp3_codec = AppConstants.get_codec_for_format('mp3')
    assert mp3_codec == 'libmp3lame'
    print(f"✓ MP3 codec: {mp3_codec}")

    # Test format checking
    is_audio = AppConstants.is_supported_format('test.mp3', 'audio')
    assert is_audio == True
    print(f"✓ MP3 is recognized as audio format")

    is_video = AppConstants.is_supported_format('test.mp4', 'video')
    assert is_video == True
    print(f"✓ MP4 is recognized as video format")

    print("AppConstants tests passed!\n")


def test_media_processor():
    """Test MediaProcessor integration"""
    print("Testing MediaProcessor...")

    processor = MediaProcessor()

    # Test supported format check
    assert processor.is_supported('test.mp3')
    print(f"✓ MediaProcessor recognizes MP3 files")

    assert processor.is_supported('test.mp4')
    print(f"✓ MediaProcessor recognizes MP4 files")

    # Test getting supported formats
    all_formats = processor.get_supported_formats('all')
    print(f"✓ Total supported formats: {len(all_formats)}")

    print("MediaProcessor tests passed!\n")


def main():
    """Run all tests"""
    print("=" * 50)
    print("Design Patterns Implementation Tests")
    print("=" * 50 + "\n")

    try:
        test_constants()
        test_factory_pattern()
        test_strategy_pattern()
        test_media_processor()

        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)