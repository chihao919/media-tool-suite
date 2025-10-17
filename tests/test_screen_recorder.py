#!/usr/bin/env python3
"""
Unit tests for screen_recorder module
"""

import unittest
import os
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from screen_recorder import ScreenRecorder, ScreenRecorderBuilder


class TestScreenRecorder(unittest.TestCase):
    """Test cases for ScreenRecorder class"""

    def setUp(self):
        """Set up test fixtures"""
        self.recorder = ScreenRecorder()
        self.test_output = "/tmp/test_recording.mp4"

    def tearDown(self):
        """Clean up after tests"""
        # Stop any running recording
        if self.recorder.is_recording:
            self.recorder.stop_recording()

        # Clean up test file
        if os.path.exists(self.test_output):
            os.remove(self.test_output)

    def test_recorder_initialization(self):
        """Test ScreenRecorder initialization"""
        self.assertIsNotNone(self.recorder)
        self.assertFalse(self.recorder.is_recording)
        self.assertIsNone(self.recorder.output_file)
        self.assertIsNone(self.recorder.recording_process)

    def test_check_ffmpeg_available(self):
        """Test ffmpeg availability check"""
        result = ScreenRecorder.check_ffmpeg_available()
        self.assertIsInstance(result, bool)
        # Note: This test assumes ffmpeg is installed
        self.assertTrue(result, "ffmpeg should be available for this test")

    def test_get_default_output_path(self):
        """Test default output path generation"""
        output_path = ScreenRecorder.get_default_output_path()
        self.assertIsInstance(output_path, str)
        self.assertTrue(output_path.endswith('.mp4'))
        self.assertIn('screen_recording_', output_path)
        # Check it points to Desktop
        self.assertIn('Desktop', output_path)

    @patch('subprocess.run')
    def test_get_available_devices(self, mock_run):
        """Test getting available devices"""
        # Mock ffmpeg device list output
        mock_output = """[AVFoundation indev @ 0x...] AVFoundation video devices:
[AVFoundation indev @ 0x...] [0] FaceTime HD Camera
[AVFoundation indev @ 0x...] [1] Capture screen 0
[AVFoundation indev @ 0x...] AVFoundation audio devices:
[AVFoundation indev @ 0x...] [0] MacBook Pro Microphone
[AVFoundation indev @ 0x...] [1] BlackHole 2ch"""

        mock_run.return_value = MagicMock(
            returncode=0,
            stderr=mock_output
        )

        devices = self.recorder.get_available_devices()

        self.assertIn('video', devices)
        self.assertIn('audio', devices)
        self.assertIsInstance(devices['video'], list)
        self.assertIsInstance(devices['audio'], list)

        # Check if devices were parsed correctly
        if devices['video']:
            self.assertIn('id', devices['video'][0])
            self.assertIn('name', devices['video'][0])

    @patch('subprocess.Popen')
    def test_start_recording_success(self, mock_popen):
        """Test successful recording start"""
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        result = self.recorder.start_recording(
            output_path=self.test_output,
            video_device="1",
            audio_device="0"
        )

        self.assertTrue(result)
        self.assertTrue(self.recorder.is_recording)
        self.assertEqual(self.recorder.output_file, self.test_output)
        mock_popen.assert_called_once()

    def test_start_recording_already_recording(self):
        """Test starting recording when already recording"""
        # Set recorder as already recording
        self.recorder.is_recording = True

        result = self.recorder.start_recording(self.test_output)

        self.assertFalse(result)

    @patch('subprocess.Popen')
    def test_stop_recording_success(self, mock_popen):
        """Test successful recording stop"""
        # Start recording first
        mock_process = MagicMock()
        mock_process.communicate.return_value = (None, None)
        mock_popen.return_value = mock_process

        self.recorder.start_recording(self.test_output)

        # Stop recording
        result = self.recorder.stop_recording()

        self.assertTrue(result)
        self.assertFalse(self.recorder.is_recording)
        mock_process.communicate.assert_called_once()

    def test_stop_recording_not_recording(self):
        """Test stopping when not recording"""
        result = self.recorder.stop_recording()
        self.assertFalse(result)

    def test_get_recording_status(self):
        """Test getting recording status"""
        status = self.recorder.get_recording_status()

        self.assertIsInstance(status, dict)
        self.assertIn('is_recording', status)
        self.assertIn('output_file', status)
        self.assertFalse(status['is_recording'])
        self.assertIsNone(status['output_file'])

    @patch('subprocess.Popen')
    def test_recording_with_progress_callback(self, mock_popen):
        """Test recording with progress callback"""
        callback = Mock()

        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stderr.readline.side_effect = [
            "frame=  100 fps=30 time=00:00:03.33",
            ""  # End of output
        ]
        mock_popen.return_value = mock_process

        result = self.recorder.start_recording(
            output_path=self.test_output,
            progress_callback=callback
        )

        self.assertTrue(result)
        # Give thread time to start
        time.sleep(0.1)


class TestScreenRecorderBuilder(unittest.TestCase):
    """Test cases for ScreenRecorderBuilder class"""

    def setUp(self):
        """Set up test fixtures"""
        self.builder = ScreenRecorderBuilder()

    def test_builder_initialization(self):
        """Test builder initialization"""
        self.assertIsNotNone(self.builder)
        self.assertIsInstance(self.builder.recorder, ScreenRecorder)

    def test_set_output_path(self):
        """Test setting output path"""
        test_path = "/tmp/test.mp4"
        result = self.builder.set_output_path(test_path)

        self.assertEqual(self.builder.output_path, test_path)
        self.assertEqual(result, self.builder)  # Check chaining

    def test_set_video_device(self):
        """Test setting video device"""
        device_id = "2"
        result = self.builder.set_video_device(device_id)

        self.assertEqual(self.builder.video_device, device_id)
        self.assertEqual(result, self.builder)

    def test_set_audio_device(self):
        """Test setting audio device"""
        device_id = "1"
        result = self.builder.set_audio_device(device_id)

        self.assertEqual(self.builder.audio_device, device_id)
        self.assertEqual(result, self.builder)

    def test_set_framerate(self):
        """Test setting framerate"""
        fps = 60
        result = self.builder.set_framerate(fps)

        self.assertEqual(self.builder.framerate, fps)
        self.assertEqual(result, self.builder)

    def test_set_quality(self):
        """Test setting quality"""
        quality = "high"
        result = self.builder.set_quality(quality)

        self.assertEqual(self.builder.video_quality, quality)
        self.assertEqual(result, self.builder)

    def test_set_quality_invalid(self):
        """Test setting invalid quality (should keep default)"""
        original_quality = self.builder.video_quality
        result = self.builder.set_quality("invalid")

        self.assertEqual(self.builder.video_quality, original_quality)
        self.assertEqual(result, self.builder)

    def test_set_progress_callback(self):
        """Test setting progress callback"""
        callback = Mock()
        result = self.builder.set_progress_callback(callback)

        self.assertEqual(self.builder.progress_callback, callback)
        self.assertEqual(result, self.builder)

    def test_build(self):
        """Test building recorder"""
        recorder = self.builder.build()

        self.assertIsInstance(recorder, ScreenRecorder)
        self.assertEqual(recorder, self.builder.recorder)

    def test_builder_chaining(self):
        """Test method chaining"""
        result = (self.builder
                  .set_output_path("/tmp/test.mp4")
                  .set_video_device("1")
                  .set_audio_device("0")
                  .set_framerate(30)
                  .set_quality("high"))

        self.assertEqual(result, self.builder)

    @patch('subprocess.Popen')
    def test_start_with_default_path(self, mock_popen):
        """Test starting recording with default output path"""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        result = self.builder.start()

        self.assertTrue(result)
        self.assertIsNotNone(self.builder.output_path)
        self.assertTrue(self.builder.output_path.endswith('.mp4'))

    @patch('subprocess.Popen')
    def test_start_with_custom_settings(self, mock_popen):
        """Test starting recording with custom settings"""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        test_path = "/tmp/custom_recording.mp4"

        result = (self.builder
                  .set_output_path(test_path)
                  .set_video_device("1")
                  .set_audio_device("0")
                  .set_framerate(60)
                  .set_quality("ultra")
                  .start())

        self.assertTrue(result)
        self.assertEqual(self.builder.recorder.output_file, test_path)


class TestScreenRecorderIntegration(unittest.TestCase):
    """Integration tests for ScreenRecorder (requires ffmpeg)"""

    @classmethod
    def setUpClass(cls):
        """Check if ffmpeg is available before running integration tests"""
        if not ScreenRecorder.check_ffmpeg_available():
            raise unittest.SkipTest("ffmpeg not available, skipping integration tests")

    def test_get_devices_integration(self):
        """Integration test: Get actual devices from system"""
        recorder = ScreenRecorder()
        devices = recorder.get_available_devices()

        self.assertIsInstance(devices, dict)
        self.assertIn('video', devices)
        self.assertIn('audio', devices)

        # On macOS, there should be at least screen capture devices
        # Note: This might fail in CI/CD without proper permissions
        print(f"Found video devices: {devices['video']}")
        print(f"Found audio devices: {devices['audio']}")


if __name__ == '__main__':
    unittest.main()
