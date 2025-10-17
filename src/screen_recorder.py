#!/usr/bin/env python3
"""
Screen Recording Module
Records screen with system audio on macOS
"""

import subprocess
import threading
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
import json


class ScreenRecorder:
    """Screen recorder using ffmpeg with avfoundation"""

    def __init__(self):
        self.recording_process: Optional[subprocess.Popen] = None
        self.is_recording = False
        self.output_file = None
        self.recording_thread = None

    def get_available_devices(self) -> dict:
        """
        Get list of available audio/video devices on macOS
        Returns dict with 'video' and 'audio' device lists
        """
        try:
            # Run ffmpeg to list devices
            cmd = ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse stderr output (ffmpeg outputs device list to stderr)
            output = result.stderr

            devices = {'video': [], 'audio': []}
            current_type = None

            for line in output.split('\n'):
                if 'AVFoundation video devices:' in line:
                    current_type = 'video'
                elif 'AVFoundation audio devices:' in line:
                    current_type = 'audio'
                elif current_type and '] [' in line:
                    # Parse device line: [AVFoundation indev @ 0x...] [0] FaceTime HD Camera
                    parts = line.split('] ')
                    if len(parts) >= 3:
                        device_id = parts[1].strip('[]')
                        device_name = parts[2].strip()
                        devices[current_type].append({
                            'id': device_id,
                            'name': device_name
                        })

            return devices

        except Exception as e:
            print(f"Error getting devices: {e}")
            return {'video': [], 'audio': []}

    def start_recording(
        self,
        output_path: str,
        video_device: str = "1",  # Default: Capture screen 1
        audio_device: str = "0",  # Default: First audio device
        framerate: int = 30,
        video_quality: str = "medium",
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Start screen recording with system audio

        Args:
            output_path: Output file path
            video_device: Video device ID (default "1" for screen capture)
            audio_device: Audio device ID (default "0" for system audio)
            framerate: Recording framerate (default 30)
            video_quality: Quality preset - "low", "medium", "high", "ultra"
            progress_callback: Callback function for progress updates

        Returns:
            bool: True if recording started successfully
        """
        if self.is_recording:
            print("Already recording")
            return False

        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            self.output_file = output_path

            # Quality presets
            quality_presets = {
                'low': {'crf': '28', 'preset': 'veryfast'},
                'medium': {'crf': '23', 'preset': 'medium'},
                'high': {'crf': '18', 'preset': 'slow'},
                'ultra': {'crf': '15', 'preset': 'slower'}
            }

            preset = quality_presets.get(video_quality, quality_presets['medium'])

            # Build ffmpeg command
            # Format: ffmpeg -f avfoundation -framerate 30 -i "<screen>:<audio>" -c:v libx264 -preset medium -crf 23 -c:a aac output.mp4
            cmd = [
                'ffmpeg',
                '-f', 'avfoundation',
                '-framerate', str(framerate),
                '-capture_cursor', '1',  # Capture mouse cursor
                '-i', f'{video_device}:{audio_device}',  # video:audio device
                '-c:v', 'libx264',  # Video codec
                '-preset', preset['preset'],
                '-crf', preset['crf'],
                '-c:a', 'aac',  # Audio codec
                '-b:a', '192k',  # Audio bitrate
                '-ar', '48000',  # Audio sample rate
                '-y',  # Overwrite output file
                output_path
            ]

            # Start recording process
            self.recording_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.is_recording = True

            # Start monitoring thread
            if progress_callback:
                self.recording_thread = threading.Thread(
                    target=self._monitor_recording,
                    args=(progress_callback,)
                )
                self.recording_thread.daemon = True
                self.recording_thread.start()

            return True

        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
            return False

    def stop_recording(self) -> bool:
        """
        Stop current recording

        Returns:
            bool: True if stopped successfully
        """
        if not self.is_recording or not self.recording_process:
            print("Not recording")
            return False

        try:
            # Send 'q' command to ffmpeg to stop gracefully
            self.recording_process.communicate(input='q\n', timeout=5)

            self.is_recording = False
            self.recording_process = None

            return True

        except subprocess.TimeoutExpired:
            # Force terminate if graceful stop fails
            self.recording_process.terminate()
            try:
                self.recording_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.recording_process.kill()

            self.is_recording = False
            self.recording_process = None
            return True

        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False

    def _monitor_recording(self, callback: Callable[[str], None]):
        """Monitor recording process and provide progress updates"""
        if not self.recording_process:
            return

        try:
            while self.is_recording and self.recording_process:
                # Read stderr output from ffmpeg
                line = self.recording_process.stderr.readline()
                if not line:
                    break

                # Parse progress information
                if 'time=' in line:
                    callback(line.strip())

        except Exception as e:
            print(f"Error monitoring recording: {e}")

    def get_recording_status(self) -> dict:
        """
        Get current recording status

        Returns:
            dict: Status information including is_recording, output_file
        """
        return {
            'is_recording': self.is_recording,
            'output_file': self.output_file
        }

    @staticmethod
    def check_ffmpeg_available() -> bool:
        """
        Check if ffmpeg is available

        Returns:
            bool: True if ffmpeg is available
        """
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def get_default_output_path() -> str:
        """
        Get default output file path with timestamp

        Returns:
            str: Default output path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screen_recording_{timestamp}.mp4"
        return str(Path.home() / "Desktop" / filename)


class ScreenRecorderBuilder:
    """Builder pattern for ScreenRecorder configuration"""

    def __init__(self):
        self.recorder = ScreenRecorder()
        self.output_path = None
        self.video_device = "1"
        self.audio_device = "0"
        self.framerate = 30
        self.video_quality = "medium"
        self.progress_callback = None

    def set_output_path(self, path: str):
        """Set output file path"""
        self.output_path = path
        return self

    def set_video_device(self, device_id: str):
        """Set video device ID"""
        self.video_device = device_id
        return self

    def set_audio_device(self, device_id: str):
        """Set audio device ID"""
        self.audio_device = device_id
        return self

    def set_framerate(self, fps: int):
        """Set recording framerate"""
        self.framerate = fps
        return self

    def set_quality(self, quality: str):
        """Set video quality preset"""
        if quality in ['low', 'medium', 'high', 'ultra']:
            self.video_quality = quality
        return self

    def set_progress_callback(self, callback: Callable[[str], None]):
        """Set progress callback function"""
        self.progress_callback = callback
        return self

    def build(self) -> ScreenRecorder:
        """Build and return configured ScreenRecorder"""
        return self.recorder

    def start(self) -> bool:
        """Build and start recording"""
        if not self.output_path:
            self.output_path = ScreenRecorder.get_default_output_path()

        return self.recorder.start_recording(
            output_path=self.output_path,
            video_device=self.video_device,
            audio_device=self.audio_device,
            framerate=self.framerate,
            video_quality=self.video_quality,
            progress_callback=self.progress_callback
        )
