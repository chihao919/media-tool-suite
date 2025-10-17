#!/usr/bin/env python3
"""
Split Progress Test
Test split functionality with progress callback
"""

import sys
import os
import tempfile
import subprocess

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from media_processor import MediaProcessorBuilder

def create_test_video(duration=10):
    """Create a small test video file using ffmpeg"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_file.close()

    try:
        # Create a very simple test video
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', f'testsrc=duration={duration}:size=160x120:rate=1',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '30',
            '-y', temp_file.name
        ]

        print(f"Creating test video: {temp_file.name}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return None

        actual_size = os.path.getsize(temp_file.name) / (1024 * 1024)
        print(f"Created test video: {actual_size:.2f}MB, Duration: {duration}s")
        return temp_file.name

    except Exception as e:
        print(f"Error creating test video: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return None

def test_split_progress():
    """Test split functionality with progress callback"""
    print("=== Testing Split Progress Callback ===")

    # Create test video
    test_video = create_test_video(duration=20)  # 20 second video
    if not test_video:
        print("❌ Failed to create test video")
        return False

    try:
        progress_updates = []

        def progress_callback(progress):
            progress_updates.append(progress)
            print(f"Progress: {progress:.1f}%")

        print(f"Created test video: {test_video}")
        print("Testing size-based split (5MB target)...")

        # Create splitter
        processor = MediaProcessorBuilder.create_splitter('size', size=5)

        output_params = {
            'keep_original': True,
            'progress_callback': progress_callback
        }

        print("Starting split operation...")
        success = processor.process_file(test_video, output_params)

        print(f"\nSplit result: {'Success' if success else 'Failed'}")
        print(f"Progress updates received: {len(progress_updates)}")

        if progress_updates:
            print(f"Progress range: {min(progress_updates):.1f}% - {max(progress_updates):.1f}%")
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

        # Also clean up any generated split files
        video_dir = os.path.dirname(test_video)
        base_name = os.path.splitext(os.path.basename(test_video))[0]
        for file in os.listdir(video_dir):
            if file.startswith(base_name + "_part"):
                part_file = os.path.join(video_dir, file)
                os.unlink(part_file)
                print(f"🧹 Cleaned up split file: {file}")

def test_duration_split():
    """Test duration-based split"""
    print("\n=== Testing Duration Split Progress ===")

    test_video = create_test_video(duration=30)  # 30 second video
    if not test_video:
        print("❌ Failed to create test video")
        return False

    try:
        progress_updates = []

        def progress_callback(progress):
            progress_updates.append(progress)
            print(f"Duration Progress: {progress:.1f}%")

        print("Testing duration-based split (10s parts)...")

        # Create duration splitter
        processor = MediaProcessorBuilder.create_splitter('duration', duration=10)

        output_params = {
            'keep_original': True,
            'progress_callback': progress_callback
        }

        success = processor.process_file(test_video, output_params)

        print(f"\nDuration split result: {'Success' if success else 'Failed'}")
        print(f"Progress updates received: {len(progress_updates)}")

        return success and len(progress_updates) > 0

    except Exception as e:
        print(f"❌ Duration test failed: {e}")
        return False

    finally:
        # Clean up
        if os.path.exists(test_video):
            os.unlink(test_video)

        # Clean up split files
        video_dir = os.path.dirname(test_video)
        base_name = os.path.splitext(os.path.basename(test_video))[0]
        for file in os.listdir(video_dir):
            if file.startswith(base_name + "_part"):
                part_file = os.path.join(video_dir, file)
                os.unlink(part_file)

if __name__ == "__main__":
    print("🎯 Split Progress Callback Test")
    print("=" * 50)

    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg detected")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not available - cannot run test")
        sys.exit(1)

    # Test size-based split
    size_result = test_split_progress()

    # Test duration-based split
    duration_result = test_duration_split()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Size-based split progress: {'✅ PASS' if size_result else '❌ FAIL'}")
    print(f"Duration-based split progress: {'✅ PASS' if duration_result else '❌ FAIL'}")

    if size_result and duration_result:
        print("\n🎉 All tests passed! Progress callbacks are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Progress callback functionality needs fixing.")

    sys.exit(0 if (size_result and duration_result) else 1)