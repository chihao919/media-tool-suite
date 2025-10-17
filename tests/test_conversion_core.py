#!/usr/bin/env python3
"""
Test core conversion functionality without UI
"""

import os
import tempfile
from media_processor import MediaProcessorBuilder
from pathlib import Path

def create_test_video():
    """Create a simple test video using FFmpeg"""
    test_file = "/tmp/test_input.mp4"

    # Create a simple 5-second test video
    cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=5:size=320x240:rate=1',
        '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=5',
        '-c:v', 'libx264', '-c:a', 'aac', '-y', test_file
    ]

    import subprocess
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Test video created: {test_file}")
        return test_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create test video: {e.stderr}")
        return None

def test_basic_conversion():
    """Test basic video conversion without progress callback"""
    print("\n=== Testing Basic Conversion (No Progress Callback) ===")

    # Create test input
    input_file = create_test_video()
    if not input_file:
        return False

    try:
        # Create converter
        processor = MediaProcessorBuilder.create_converter(
            format='avi',
            video_bitrate='1M',
            audio_bitrate='128k'
        )

        output_file = "/tmp/test_output_basic.avi"
        output_params = {
            'output_file': output_file,
            'output_dir': '/tmp',
            'naming_style': 'original'
        }

        print(f"Input: {input_file}")
        print(f"Output: {output_file}")

        # Test conversion
        success = processor.process_file(input_file, output_params)

        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ Basic conversion successful! Output size: {file_size} bytes")
            return True
        else:
            print(f"❌ Basic conversion failed! Success: {success}, File exists: {os.path.exists(output_file)}")
            return False

    except Exception as e:
        print(f"❌ Exception during basic conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_progress_callback_conversion():
    """Test conversion with progress callback"""
    print("\n=== Testing Conversion with Progress Callback ===")

    # Create test input
    input_file = create_test_video()
    if not input_file:
        return False

    progress_updates = []

    def progress_callback(percent):
        progress_updates.append(percent)
        print(f"Progress: {percent:.1f}%")

    try:
        # Create converter
        processor = MediaProcessorBuilder.create_converter(
            format='avi',
            video_bitrate='1M',
            audio_bitrate='128k'
        )

        output_file = "/tmp/test_output_progress.avi"
        output_params = {
            'output_file': output_file,
            'output_dir': '/tmp',
            'naming_style': 'original',
            'progress_callback': progress_callback
        }

        print(f"Input: {input_file}")
        print(f"Output: {output_file}")

        # Test conversion
        success = processor.process_file(input_file, output_params)

        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ Progress conversion successful! Output size: {file_size} bytes")
            print(f"Progress updates received: {len(progress_updates)}")
            if progress_updates:
                print(f"Progress range: {min(progress_updates):.1f}% - {max(progress_updates):.1f}%")
            return True
        else:
            print(f"❌ Progress conversion failed! Success: {success}, File exists: {os.path.exists(output_file)}")
            print(f"Progress updates received: {len(progress_updates)}")
            return False

    except Exception as e:
        print(f"❌ Exception during progress conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_support():
    """Test file format support detection"""
    print("\n=== Testing File Format Support ===")

    from media_handlers import MediaHandlerFactory
    factory = MediaHandlerFactory()

    test_files = [
        "test.mp4",
        "test.avi",
        "test.mkv",
        "test.mov",
        "test.mp3",
        "test.wav",
        "test.unsupported"
    ]

    for filename in test_files:
        supported = factory.is_supported(filename)
        handler = factory.create_handler(filename) if supported else None
        print(f"{filename}: {'✅' if supported else '❌'} {handler.__class__.__name__ if handler else 'No handler'}")

def main():
    """Run all core functionality tests"""
    print("🚀 Testing Core Conversion Functionality")
    print("=" * 50)

    # Test file support first
    test_file_support()

    # Test basic conversion
    basic_success = test_basic_conversion()

    # Test progress callback conversion
    progress_success = test_progress_callback_conversion()

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Basic Conversion: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Progress Conversion: {'✅ PASS' if progress_success else '❌ FAIL'}")

    if basic_success and progress_success:
        print("\n🎉 All core functionality tests PASSED!")
        print("The issue is likely in the UI layer.")
    else:
        print("\n⚠️ Core functionality issues detected!")
        print("The problem is in the conversion logic, not the UI.")

    return basic_success and progress_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)