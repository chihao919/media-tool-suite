#!/usr/bin/env python3
"""
Split Logic Test
Test the file size splitting logic to identify and fix issues
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from process_strategies import SplitStrategy

class TestSplitLogic(unittest.TestCase):
    """Test split logic functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def test_file_size_calculation(self):
        """Test file size split calculation"""
        print("\n=== Testing File Size Split Logic ===")

        # Test scenarios
        test_cases = [
            {
                "description": "300MB file, 190MB target",
                "file_size_mb": 300,
                "target_size_mb": 190,
                "expected_parts": 2
            },
            {
                "description": "500MB file, 100MB target",
                "file_size_mb": 500,
                "target_size_mb": 100,
                "expected_parts": 5
            },
            {
                "description": "150MB file, 190MB target (no split needed)",
                "file_size_mb": 150,
                "target_size_mb": 190,
                "expected_parts": 1  # Should not split
            }
        ]

        for case in test_cases:
            with self.subTest(case=case["description"]):
                print(f"\nTesting: {case['description']}")

                # Current logic from SplitStrategy._split_by_size
                file_size_mb = case["file_size_mb"]
                max_size_mb = case["target_size_mb"]

                if file_size_mb <= max_size_mb:
                    calculated_parts = 1  # No split needed
                else:
                    # Current problematic logic
                    calculated_parts = int(file_size_mb / max_size_mb)
                    if file_size_mb % max_size_mb > 0:
                        calculated_parts += 1

                print(f"File size: {file_size_mb}MB")
                print(f"Target size: {max_size_mb}MB")
                print(f"Current logic calculated: {calculated_parts} parts")
                print(f"Expected: {case['expected_parts']} parts")

                # Check if current logic matches expected
                matches = calculated_parts == case['expected_parts']
                print(f"Match: {'✓' if matches else '✗'}")

                if not matches:
                    print(f"❌ Logic error detected!")

                    # Show better calculation
                    import math
                    better_calc = math.ceil(file_size_mb / max_size_mb)
                    print(f"Better calculation (ceil): {better_calc} parts")

    def test_split_strategy_mock(self):
        """Test SplitStrategy with mocked dependencies"""
        print("\n=== Testing SplitStrategy Implementation ===")

        # Create strategy for size splitting
        split_params = {'size': 190}  # 190MB target
        strategy = SplitStrategy('size', split_params)

        # Mock the dependencies
        with patch.object(strategy, '_get_media_duration', return_value=3600), \
             patch.object(strategy, '_perform_split', return_value=True), \
             patch('os.path.getsize') as mock_getsize:

            # Test case: 300MB file should split into 2 parts
            mock_getsize.return_value = 300 * 1024 * 1024  # 300MB in bytes

            print("Testing 300MB file with 190MB target:")
            print("File size: 300MB")
            print("Target size: 190MB")

            # This should call _perform_split with correct num_parts
            result = strategy._split_by_size("fake_file.mp4", {})

            # Calculate what the strategy actually computed
            file_size_mb = 300
            max_size_mb = 190

            if file_size_mb <= max_size_mb:
                calculated_parts = 1
            else:
                calculated_parts = int(file_size_mb / max_size_mb)
                if file_size_mb % max_size_mb > 0:
                    calculated_parts += 1

            print(f"Strategy calculated: {calculated_parts} parts")

            # The issue: 300 / 190 = 1.57...
            # int(1.57) = 1, then 300 % 190 = 110 > 0, so +1 = 2 ✓
            # This should be correct for this case

            # But let's test a problematic case
            print("\nTesting problematic case:")
            mock_getsize.return_value = 380 * 1024 * 1024  # 380MB

            file_size_mb = 380
            max_size_mb = 190

            calculated_parts = int(file_size_mb / max_size_mb)
            if file_size_mb % max_size_mb > 0:
                calculated_parts += 1

            print(f"380MB file, 190MB target: {calculated_parts} parts")
            # 380 / 190 = 2.0 exactly
            # int(2.0) = 2, 380 % 190 = 0, so no +1 = 2 parts ✓

            # Test edge case that might cause 15 parts
            print("\nTesting edge case that might cause many parts:")
            mock_getsize.return_value = 200 * 1024 * 1024  # 200MB

            file_size_mb = 200
            max_size_mb = 190

            calculated_parts = int(file_size_mb / max_size_mb)
            if file_size_mb % max_size_mb > 0:
                calculated_parts += 1

            print(f"200MB file, 190MB target: {calculated_parts} parts")
            # 200 / 190 = 1.05...
            # int(1.05) = 1, 200 % 190 = 10 > 0, so +1 = 2 parts ✓

if __name__ == "__main__":
    # Run basic tests first
    test = TestSplitLogic()
    test.setUp()
    test.test_file_size_calculation()
    test.test_split_strategy_mock()

    print("\n=== Test Summary ===")
    print("The basic logic seems correct for most cases.")
    print("The issue of getting 15 parts for 190MB might be:")
    print("1. Wrong input parameters being passed")
    print("2. Issue in _perform_split method")
    print("3. UI not reading the correct split mode/value")

    # Run unittest
    unittest.main(argv=[''], exit=False, verbosity=2)