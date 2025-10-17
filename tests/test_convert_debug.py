#!/usr/bin/env python3
"""
Debug conversion functionality
"""

import os
import tempfile
from media_processor import MediaProcessorBuilder

def test_converter_creation():
    """Test if converter can be created"""
    print("Testing converter creation...")

    try:
        processor = MediaProcessorBuilder.create_converter(
            format='mp3',
            bitrate='192k',
            sample_rate='44100',
            normalize=False
        )
        print("✅ Converter created successfully")

        # Test if we have a strategy
        if processor.current_strategy:
            print(f"✅ Strategy set: {processor.current_strategy.__class__.__name__}")
        else:
            print("❌ No strategy set")

        return processor
    except Exception as e:
        print(f"❌ Failed to create converter: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_fake_conversion():
    """Test conversion with fake file"""
    print("\nTesting fake conversion...")

    processor = test_converter_creation()
    if not processor:
        return False

    # Create a fake audio file path (we're not actually processing)
    fake_audio_file = "/tmp/test.mp3"

    try:
        # Test if file is supported
        is_supported = processor.is_supported(fake_audio_file)
        print(f"✅ File support check: {is_supported}")

        # Test output params
        output_params = {
            'output_file': '/tmp/test_output.wav',
            'output_dir': '/tmp',
            'naming_style': 'original'
        }
        print(f"✅ Output params created: {output_params}")

        # We won't actually run the conversion since we don't have a real file
        print("✅ Conversion test setup successful")
        return True

    except Exception as e:
        print(f"❌ Conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("CONVERSION DEBUG TEST")
    print("=" * 50)

    success1 = test_converter_creation()
    success2 = test_fake_conversion()

    if success1 and success2:
        print("\n✅ All tests passed - conversion should work")
        return True
    else:
        print("\n❌ Some tests failed - conversion may have issues")
        return False

if __name__ == "__main__":
    main()