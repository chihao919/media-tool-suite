#!/usr/bin/env python3
"""
Test Small File Split
Test splitting logic with a file smaller than target size
"""

import sys
import os
import tempfile

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from process_strategies import SplitStrategy

def create_test_file(size_mb=120):
    """Create a test file of specified size (in MB)"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)

    # Create a file of approximately the specified size
    chunk_size = 1024 * 1024  # 1MB chunks
    for _ in range(size_mb):
        temp_file.write(b'0' * chunk_size)

    temp_file.close()
    return temp_file.name

def test_small_file_split():
    """Test splitting a file smaller than target size"""
    print("🧪 Testing Small File Split (< 150MB)")
    print("=" * 50)

    # Create a 120MB test file
    test_file = create_test_file(120)
    file_size_mb = os.path.getsize(test_file) / (1024 * 1024)

    print(f"Created test file: {test_file}")
    print(f"File size: {file_size_mb:.2f}MB")

    try:
        # Test case: 120MB file with 190MB target
        print(f"\n📋 Test Case: {file_size_mb:.0f}MB file, 190MB target")
        split_params = {'size': 190}
        strategy = SplitStrategy('size', split_params)

        print("Calling _split_by_size...")
        result = strategy._split_by_size(test_file, {'keep_original': True})

        print(f"Result: {'Success' if result else 'Failed'}")

        # Manual calculation verification
        print(f"\n🔍 Manual Verification:")
        if file_size_mb <= 190:
            print(f"  {file_size_mb:.0f}MB <= 190MB → Should NOT split")
            print(f"  Expected: No split needed")
        else:
            parts = int(file_size_mb / 190)
            if file_size_mb % 190 > 0:
                parts += 1
            print(f"  Should split into {parts} parts")

        return result

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)
            print(f"\n🧹 Cleaned up test file")

def test_multiple_sizes():
    """Test multiple file sizes with 190MB target"""
    print("\n🧪 Testing Multiple File Sizes with 190MB Target")
    print("=" * 55)

    test_sizes = [100, 120, 150, 200, 300, 500]  # MB
    target_size = 190

    for size_mb in test_sizes:
        print(f"\n📋 Test: {size_mb}MB file")

        # Manual calculation
        if size_mb <= target_size:
            expected_parts = 1
            should_split = "No"
        else:
            expected_parts = int(size_mb / target_size)
            if size_mb % target_size > 0:
                expected_parts += 1
            should_split = "Yes"

        print(f"  Target: {target_size}MB")
        print(f"  Should split: {should_split}")
        print(f"  Expected parts: {expected_parts}")

        # Test with actual file
        test_file = create_test_file(size_mb)
        actual_size = os.path.getsize(test_file) / (1024 * 1024)

        try:
            split_params = {'size': target_size}
            strategy = SplitStrategy('size', split_params)

            print(f"  Actual file size: {actual_size:.2f}MB")
            result = strategy._split_by_size(test_file, {'keep_original': True})
            print(f"  Split result: {'Success' if result else 'Failed'}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

if __name__ == "__main__":
    print("🎯 Small File Split Test Suite")
    print("=" * 50)

    # Test 1: Single small file
    test_small_file_split()

    # Test 2: Multiple sizes
    test_multiple_sizes()

    print("\n✅ All tests completed!")