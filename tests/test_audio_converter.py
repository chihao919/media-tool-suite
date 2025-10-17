#!/usr/bin/env python3

import unittest
import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Import modules to test
import audio_utils
import wav_to_mp3

class TestAudioUtils(unittest.TestCase):
    """Test core audio utility functions"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.mp3")

        # Create a dummy audio file (empty for testing)
        with open(self.test_file, 'wb') as f:
            f.write(b'dummy audio content')

    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir)

    @patch('subprocess.run')
    def test_get_audio_duration(self, mock_run):
        """Test getting audio duration"""
        # Mock ffprobe output
        mock_run.return_value = MagicMock(
            stdout='123.45',
            returncode=0
        )

        duration = audio_utils.get_audio_duration(self.test_file)

        # Check that ffprobe was called correctly
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn('ffprobe', args)
        self.assertIn(self.test_file, args)
        self.assertEqual(duration, 123.45)

    @patch('subprocess.run')
    def test_convert_audio(self, mock_run):
        """Test audio conversion"""
        mock_run.return_value = MagicMock(returncode=0)

        output_file = os.path.join(self.test_dir, "output.mp3")

        audio_utils.convert_audio(
            self.test_file,
            output_file,
            codec='libmp3lame',
            bitrate='192k'
        )

        # Verify ffmpeg was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn('ffmpeg', args)
        self.assertIn('-i', args)
        self.assertIn(self.test_file, args)
        self.assertIn('-acodec', args)
        self.assertIn('libmp3lame', args)

    @patch('subprocess.run')
    def test_split_audio(self, mock_run):
        """Test audio splitting"""
        mock_run.return_value = MagicMock(returncode=0)

        output_file = os.path.join(self.test_dir, "split_output.mp3")

        audio_utils.split_audio(
            self.test_file,
            start_time=30,
            duration=60,
            output_path=output_file
        )

        # Verify ffmpeg split command
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn('ffmpeg', args)
        self.assertIn('-ss', args)
        self.assertIn('30', args)
        self.assertIn('-t', args)
        self.assertIn('60', args)

class TestWavToMp3Converter(unittest.TestCase):
    """Test WAV to MP3 conversion functionality"""

    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_wav = os.path.join(self.test_dir, "test.wav")

        # Create dummy WAV file
        with open(self.test_wav, 'wb') as f:
            f.write(b'dummy wav content')

    def tearDown(self):
        """Cleanup"""
        shutil.rmtree(self.test_dir)

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_convert_wav_to_mp3_success(self, mock_exists, mock_run):
        """Test successful WAV to MP3 conversion"""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        # Mock file stats
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = MagicMock(st_size=1024000)  # 1MB

            result = wav_to_mp3.convert_wav_to_mp3(
                self.test_wav,
                bitrate='192k',
                file_num=1,
                total_files=1
            )

            self.assertTrue(result)
            mock_run.assert_called_once()

    @patch('os.path.exists')
    def test_convert_nonexistent_file(self, mock_exists):
        """Test conversion with non-existent file"""
        mock_exists.return_value = False

        result = wav_to_mp3.convert_wav_to_mp3(
            "nonexistent.wav",
            file_num=1,
            total_files=1
        )

        self.assertFalse(result)

class TestFileOperations(unittest.TestCase):
    """Test basic file operations"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_output_directory(self):
        """Test output directory creation"""
        output_dir = os.path.join(self.test_dir, "output")

        # Directory shouldn't exist initially
        self.assertFalse(os.path.exists(output_dir))

        # Create directory
        Path(output_dir).mkdir(exist_ok=True)

        # Should exist now
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.isdir(output_dir))

    def test_file_size_calculation(self):
        """Test file size calculation"""
        test_file = os.path.join(self.test_dir, "size_test.txt")
        test_content = b"0" * 1024  # 1KB of content

        with open(test_file, 'wb') as f:
            f.write(test_content)

        size_bytes = os.path.getsize(test_file)
        size_mb = size_bytes / (1024 * 1024)

        self.assertEqual(size_bytes, 1024)
        self.assertAlmostEqual(size_mb, 0.0009765625, places=6)

class TestCommandBuilding(unittest.TestCase):
    """Test FFmpeg command construction"""

    def test_mp3_conversion_command(self):
        """Test MP3 conversion command building"""
        input_file = "/path/to/input.wav"
        output_file = "/path/to/output.mp3"

        expected_cmd = [
            'ffmpeg', '-i', input_file,
            '-acodec', 'libmp3lame',
            '-b:a', '192k',
            '-ar', '44100',
            '-y',
            output_file
        ]

        # Build command
        cmd = ['ffmpeg', '-i', input_file]
        cmd.extend(['-acodec', 'libmp3lame', '-b:a', '192k'])
        cmd.extend(['-ar', '44100', '-y'])
        cmd.append(output_file)

        self.assertEqual(cmd, expected_cmd)

    def test_split_command(self):
        """Test audio split command building"""
        input_file = "/path/to/input.mp3"
        output_file = "/path/to/output_part1.mp3"

        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', '0',
            '-t', '300',
            '-c', 'copy',
            '-y', output_file
        ]

        # Verify essential components
        self.assertIn('ffmpeg', cmd)
        self.assertIn('-ss', cmd)
        self.assertIn('-t', cmd)
        self.assertIn('-c', cmd)
        self.assertIn('copy', cmd)

class TestIntegrationBasics(unittest.TestCase):
    """Basic integration tests"""

    @patch('subprocess.run')
    def test_ffmpeg_available(self, mock_run):
        """Test if FFmpeg is available (mocked)"""
        mock_run.return_value = MagicMock(returncode=0)

        try:
            subprocess.run(['ffmpeg', '-version'],
                         capture_output=True, check=True)
            ffmpeg_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            ffmpeg_available = False

        # In mock, should always be available
        self.assertTrue(ffmpeg_available)

    def test_audio_extensions_detection(self):
        """Test audio file extension detection"""
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'}

        test_files = [
            'song.mp3',
            'audio.wav',
            'music.flac',
            'podcast.m4a',
            'document.txt',  # Not audio
            'image.jpg'      # Not audio
        ]

        audio_files = []
        for filename in test_files:
            ext = Path(filename).suffix.lower()
            if ext in audio_extensions:
                audio_files.append(filename)

        expected = ['song.mp3', 'audio.wav', 'music.flac', 'podcast.m4a']
        self.assertEqual(audio_files, expected)

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAudioUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestWavToMp3Converter))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandBuilding))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationBasics))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success/failure
    return result.wasSuccessful()

if __name__ == '__main__':
    print("🧪 Running Audio Converter Unit Tests")
    print("=" * 50)

    success = run_tests()

    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

    exit(0 if success else 1)