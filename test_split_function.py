#!/usr/bin/env python3
"""
Test Split Function
Direct testing of split functionality with debug output
"""

import sys
import os
import tempfile
import subprocess

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from process_strategies import SplitStrategy

def create_test_video(size_mb=200, duration_seconds=1800):
    """Create a test video file using ffmpeg"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_file.close()

    try:
        # Create a test video using ffmpeg
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', f'testsrc=duration={duration_seconds}:size=320x240:rate=1',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-y', temp_file.name
        ]

        print(f"Creating test video: {temp_file.name}")
        print(f"Target size: {size_mb}MB, Duration: {duration_seconds}s")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return None

        # Check actual file size
        actual_size = os.path.getsize(temp_file.name) / (1024 * 1024)
        print(f"Created video: {actual_size:.2f}MB")

        return temp_file.name

    except Exception as e:
        print(f"Error creating test video: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return None

def test_split_by_size_function():
    """Test the _split_by_size function directly"""
    print("🧪 Testing Split by Size Function")
    print("=" * 50)

    # Create test video
    test_video = create_test_video(size_mb=300, duration_seconds=1800)  # 30 minutes
    if not test_video:
        print("❌ Failed to create test video")
        return False

    try:
        # Test case 1: 190MB target
        print("\n📋 Test Case 1: 190MB target size")
        split_params = {'size': 190}
        strategy = SplitStrategy('size', split_params)

        print("Calling _split_by_size...")
        result = strategy._split_by_size(test_video, {'keep_original': True})
        print(f"Result: {'Success' if result else 'Failed'}")

        # Test case 2: 100MB target
        print("\n📋 Test Case 2: 100MB target size")
        split_params = {'size': 100}
        strategy = SplitStrategy('size', split_params)

        print("Calling _split_by_size...")
        result = strategy._split_by_size(test_video, {'keep_original': True})
        print(f"Result: {'Success' if result else 'Failed'}")

        # Test case 3: 50MB target (should create many parts)
        print("\n📋 Test Case 3: 50MB target size")
        split_params = {'size': 50}
        strategy = SplitStrategy('size', split_params)

        print("Calling _split_by_size...")
        result = strategy._split_by_size(test_video, {'keep_original': True})
        print(f"Result: {'Success' if result else 'Failed'}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up
        if os.path.exists(test_video):
            os.unlink(test_video)
            print(f"\n🧹 Cleaned up test file: {test_video}")

def test_manual_calculation():
    """Test manual calculation without video creation"""
    print("\n🧮 Manual Calculation Test")
    print("=" * 30)

    # Simulate different file sizes and targets
    test_cases = [
        {"file_mb": 300, "target_mb": 190},
        {"file_mb": 1500, "target_mb": 190},  # Large file
        {"file_mb": 500, "target_mb": 100},
        {"file_mb": 200, "target_mb": 50},   # This might create many parts
    ]

    for case in test_cases:
        file_size_mb = case["file_mb"]
        max_size_mb = case["target_mb"]

        print(f"\nFile: {file_size_mb}MB, Target: {max_size_mb}MB")

        if file_size_mb <= max_size_mb:
            num_parts = 1
            print("  No split needed")
        else:
            num_parts = int(file_size_mb / max_size_mb)
            if file_size_mb % max_size_mb > 0:
                num_parts += 1

            print(f"  Calculation: {file_size_mb} / {max_size_mb} = {file_size_mb / max_size_mb:.2f}")
            print(f"  int({file_size_mb / max_size_mb:.2f}) = {int(file_size_mb / max_size_mb)}")
            print(f"  Remainder: {file_size_mb % max_size_mb}")
            print(f"  Final parts: {num_parts}")

if __name__ == "__main__":
    print("🎬 Split Function Test Suite")
    print("=" * 50)

    # First test manual calculations
    test_manual_calculation()

    # Check if ffmpeg is available for video test
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("\n✅ FFmpeg detected - running video test")
        test_split_by_size_function()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠️  FFmpeg not available - skipping video creation test")
        print("Manual calculation test completed above")