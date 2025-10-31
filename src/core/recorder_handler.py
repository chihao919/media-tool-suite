"""Screen recording operations"""
from tkinter import messagebox
from screen_recorder import ScreenRecorder, ScreenRecorderBuilder


class RecorderHandler:
    """Handles screen recording operations"""

    def __init__(self, app):
        self.app = app
        self.screen_recorder = None
        self.is_recording = False
        self.recording_start_time = 0

    def refresh_recording_devices(self, show_message=True):
        """Refresh available recording devices"""
        try:
            if not self.screen_recorder:
                self.screen_recorder = ScreenRecorder()

            devices = self.screen_recorder.get_available_devices()

            # Update video device combo
            video_devices = ["1: Capture screen 1"]  # Default option
            if devices['video']:
                video_devices = [f"{d['id']}: {d['name']}" for d in devices['video']]
            self.app.recording_tab.video_device_combo['values'] = video_devices
            if video_devices:
                self.app.recording_tab.video_device_combo.current(0)

            # Update audio device combo
            audio_devices = ["0: Default Audio"]  # Default option
            if devices['audio']:
                audio_devices = [f"{d['id']}: {d['name']}" for d in devices['audio']]
            self.app.recording_tab.audio_device_combo['values'] = audio_devices
            if audio_devices:
                self.app.recording_tab.audio_device_combo.current(0)

            # Only show message if explicitly requested (e.g., manual refresh button click)
            if show_message:
                messagebox.showinfo("Success", f"Found {len(video_devices)} video and {len(audio_devices)} audio devices")

        except Exception as e:
            if show_message:
                messagebox.showerror("Error", f"Failed to refresh devices: {str(e)}")

    def start_recording(self):
        """Start screen recording"""
        try:
            # Check if ffmpeg is available
            if not ScreenRecorder.check_ffmpeg_available():
                messagebox.showerror(
                    "Error",
                    "ffmpeg is not installed or not found in PATH.\n"
                    "Please install ffmpeg to use screen recording."
                )
                return

            # Get device IDs from combo box selections
            video_device_text = self.app.recording_video_device.get()
            audio_device_text = self.app.recording_audio_device.get()

            # Extract device ID (format: "ID: Name")
            video_device = video_device_text.split(":")[0] if video_device_text else "1"
            audio_device = audio_device_text.split(":")[0] if audio_device_text else "0"

            # Get output path
            output_path = ScreenRecorder.get_default_output_path()

            # Create recorder with builder pattern
            success = (ScreenRecorderBuilder()
                      .set_output_path(output_path)
                      .set_video_device(video_device)
                      .set_audio_device(audio_device)
                      .set_framerate(int(self.app.recording_framerate.get()))
                      .set_quality(self.app.recording_quality.get())
                      .set_progress_callback(self.update_recording_progress)
                      .start())

            if success:
                self.is_recording = True
                self.app.recording_tab.status_label.config(text="🔴 Recording...", foreground="red")
                self.app.recording_tab.start_button.config(state="disabled")
                self.app.recording_tab.stop_button.config(state="normal")
                self.app.recording_tab.output_label.config(text=f"Saving to: {output_path}")

                # Start timer
                self.recording_start_time = 0
                self.update_recording_timer()
            else:
                messagebox.showerror("Error", "Failed to start recording")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")

    def stop_recording(self):
        """Stop screen recording"""
        try:
            if self.screen_recorder:
                success = self.screen_recorder.stop_recording()

                if success:
                    self.is_recording = False
                    self.app.recording_tab.status_label.config(text="✅ Recording saved", foreground="green")
                    self.app.recording_tab.start_button.config(state="normal")
                    self.app.recording_tab.stop_button.config(state="disabled")

                    # Reset timer after a delay
                    self.app.root.after(2000, lambda: self.app.recording_tab.status_label.config(
                        text="Ready to record",
                        foreground="black"
                    ))

                    messagebox.showinfo("Success", "Recording saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to stop recording")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")

    def update_recording_progress(self, progress_info):
        """Update recording progress display"""
        # This is called from the recording thread
        # Parse ffmpeg progress output if needed
        pass

    def update_recording_timer(self):
        """Update recording timer display"""
        if self.is_recording:
            self.recording_start_time += 1
            hours = self.recording_start_time // 3600
            minutes = (self.recording_start_time % 3600) // 60
            seconds = self.recording_start_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.app.recording_tab.time_label.config(text=time_str)
            # Update every second
            self.app.root.after(1000, self.update_recording_timer)
