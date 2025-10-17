#!/usr/bin/env python3
"""
Size Split Progress Test
Create a larger file to test size-based splitting progress
"""

import sys
import os
import tempfile
import subprocess

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from media_processor import MediaProcessorBuilder

def create_large_test_video(target_mb=20):
    """Create a larger test video file"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_file.close()

    try:
        # Create a longer video to reach target size
        # Estimate duration based on target size
        # At low quality, roughly 1MB per 60 seconds
        duration = target_mb * 60

        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', f'testsrc=duration={duration}:size=320x240:rate=1',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35',  # Lower quality for larger file
            '-y', temp_file.name
        ]

        print(f"Creating large test video: {temp_file.name}")
        print(f"Target size: {target_mb}MB, Duration: {duration}s")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return None

        actual_size = os.path.getsize(temp_file.name) / (1024 * 1024)
        print(f"Created test video: {actual_size:.2f}MB, Duration: {duration}s")

        if actual_size < 5:  # If still too small, try different approach
            print("File still too small, trying alternative approach...")
            os.unlink(temp_file.name)

            # Create with higher bitrate
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_file.close()

            cmd = [
                'ffmpeg', '-f', 'lavfi', '-i', f'testsrc=duration=60:size=640x480:rate=30',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-b:v', '1000k',  # Fixed bitrate
                '-y', temp_file.name
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"FFmpeg error (attempt 2): {result.stderr}")
                return None

            actual_size = os.path.getsize(temp_file.name) / (1024 * 1024)
            print(f"Created test video (attempt 2): {actual_size:.2f}MB")

        return temp_file.name

    except Exception as e:
        print(f"Error creating test video: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return None

def test_size_split_progress():
    """Test size-based split with progress callback"""
    print("=== Testing Size Split Progress with Large File ===")

    # Create a large test video
    test_video = create_large_test_video(target_mb=15)
    if not test_video:
        print("❌ Failed to create large test video")
        return False

    try:
        file_size = os.path.getsize(test_video) / (1024 * 1024)
        print(f"Test video size: {file_size:.2f}MB")

        if file_size < 8:  # If file is still small
            print(f"⚠️  File size {file_size:.2f}MB might be too small for meaningful split test")

        progress_updates = []

        def progress_callback(progress):
            progress_updates.append(progress)
            print(f"Size Split Progress: {progress:.1f}%")

        print("Testing size-based split (5MB target)...")

        # Create splitter
        processor = MediaProcessorBuilder.create_splitter('size', size=5)

        output_params = {
            'keep_original': True,
            'progress_callback': progress_callback
        }

        print("Starting split operation...")
        success = processor.process_file(test_video, output_params)

        print(f"\nSize split result: {'Success' if success else 'Failed'}")
        print(f"Progress updates received: {len(progress_updates)}")

        if progress_updates:
            print(f"Progress range: {min(progress_updates):.1f}% - {max(progress_updates):.1f}%")
            print(f"All progress updates: {[f'{p:.1f}%' for p in progress_updates]}")
        else:
            print("❌ No progress updates received!")

        return success and len(progress_updates) > 0

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up
        if os.path.exists(test_video):
            os.unlink(test_video)
            print(f"🧹 Cleaned up test video")

        # Clean up split files
        video_dir = os.path.dirname(test_video)
        base_name = os.path.splitext(os.path.basename(test_video))[0]
        for file in os.listdir(video_dir):
            if file.startswith(base_name + "_part"):
                part_file = os.path.join(video_dir, file)
                os.unlink(part_file)
                print(f"🧹 Cleaned up split file: {file}")

if __name__ == "__main__":
    print("🎯 Size Split Progress Test")
    print("=" * 50)

    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg detected")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not available - cannot run test")
        sys.exit(1)

    # Test size-based split with large file
    result = test_size_split_progress()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Size-based split progress: {'✅ PASS' if result else '❌ FAIL'}")

    if result:
        print("\n🎉 Size split progress callback test passed!")
    else:
        print("\n⚠️  Size split progress test failed.")

    sys.exit(0 if result else 1)