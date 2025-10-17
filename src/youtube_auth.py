#!/usr/bin/env python3
"""
YouTube Authentication Module
Handles YouTube login via embedded browser window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Callable

try:
    import tkinterweb
    TKINTERWEB_AVAILABLE = True
except ImportError:
    TKINTERWEB_AVAILABLE = False
    # Fallback to using system browser
    import webbrowser

class YouTubeAuthWindow:
    """YouTube authentication window with embedded browser"""

    def __init__(self, parent=None):
        """Initialize authentication window"""
        self.parent = parent
        self.cookies_file = None
        self.authenticated = False

    def show_login(self, url: str, callback: Optional[Callable] = None):
        """
        Show login window for YouTube authentication

        Args:
            url: The YouTube URL requiring authentication
            callback: Optional callback function when authentication completes
        """
        if not TKINTERWEB_AVAILABLE:
            # Fallback to system browser
            import webbrowser
            webbrowser.open(url)

            # Show dialog to inform user
            if self.parent:
                messagebox.showinfo(
                    "YouTube 登入",
                    "瀏覽器已開啟！\n\n"
                    "請在瀏覽器中：\n"
                    "1. 登入您的 YouTube 帳號\n"
                    "2. 觀看影片以通過年齡驗證\n"
                    "3. 完成後關閉此視窗並重試下載",
                    parent=self.parent
                )
            return

        # Create authentication window with embedded browser
        self.auth_window = tk.Toplevel(self.parent)
        self.auth_window.title("YouTube 登入")
        self.auth_window.geometry("900x700")

        # Center the window
        if self.parent:
            self.auth_window.transient(self.parent)
            x = self.parent.winfo_x() + 50
            y = self.parent.winfo_y() + 50
            self.auth_window.geometry(f"+{x}+{y}")

        # Create frame for browser
        browser_frame = ttk.Frame(self.auth_window)
        browser_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create embedded browser
        from tkinterweb import HtmlFrame
        self.browser = HtmlFrame(browser_frame)
        self.browser.pack(fill=tk.BOTH, expand=True)

        # Load YouTube URL
        self.browser.load_url(url)

        # Create button frame
        button_frame = ttk.Frame(self.auth_window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Instructions label
        instructions = ttk.Label(
            button_frame,
            text="請登入 YouTube 並觀看影片以通過年齡驗證",
            font=('Arial', 10)
        )
        instructions.pack(side=tk.LEFT, padx=5)

        # Complete button
        complete_btn = ttk.Button(
            button_frame,
            text="完成登入",
            command=lambda: self._on_login_complete(callback)
        )
        complete_btn.pack(side=tk.RIGHT, padx=5)

        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="取消",
            command=self.auth_window.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def _on_login_complete(self, callback: Optional[Callable]):
        """Handle login completion"""
        self.authenticated = True

        # Save cookies if possible
        if TKINTERWEB_AVAILABLE:
            try:
                # Try to extract cookies from embedded browser
                # This would need proper implementation based on tkinterweb API
                pass
            except Exception as e:
                print(f"無法儲存 cookies: {e}")

        # Close window
        if hasattr(self, 'auth_window'):
            self.auth_window.destroy()

        # Call callback if provided
        if callback:
            callback(self.authenticated)

    def get_cookies_file(self) -> Optional[str]:
        """Get path to cookies file"""
        return self.cookies_file


class SimplifiedYouTubeAuth:
    """Simplified authentication using system browser with better UX"""

    @staticmethod
    def request_login(url: str, parent_window=None) -> bool:
        """
        Request user to login via browser with improved dialog

        Args:
            url: YouTube URL to open
            parent_window: Parent tkinter window for dialog

        Returns:
            True if user confirms login completion
        """
        import webbrowser

        # Open browser
        webbrowser.open(url)

        if parent_window:
            # Create custom dialog
            dialog = tk.Toplevel(parent_window)
            dialog.title("YouTube 年齡驗證")
            dialog.geometry("400x200")
            dialog.resizable(False, False)

            # Center dialog
            dialog.transient(parent_window)
            parent_window.update_idletasks()
            x = parent_window.winfo_x() + (parent_window.winfo_width() // 2) - 200
            y = parent_window.winfo_y() + (parent_window.winfo_height() // 2) - 100
            dialog.geometry(f"+{x}+{y}")

            # Create content
            frame = ttk.Frame(dialog, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)

            # Icon and title
            title_label = ttk.Label(
                frame,
                text="🔞 需要年齡驗證",
                font=('Arial', 14, 'bold')
            )
            title_label.pack(pady=(0, 10))

            # Instructions
            instructions = ttk.Label(
                frame,
                text="瀏覽器已開啟！請完成以下步驟：\n\n"
                     "1. 登入您的 YouTube 帳號\n"
                     "2. 播放影片以通過年齡驗證\n"
                     "3. 完成後點擊下方按鈕",
                justify=tk.LEFT
            )
            instructions.pack(pady=(0, 15))

            # Result variable
            result = {'completed': False}

            def on_complete():
                result['completed'] = True
                dialog.destroy()

            def on_cancel():
                dialog.destroy()

            # Buttons
            btn_frame = ttk.Frame(frame)
            btn_frame.pack()

            complete_btn = ttk.Button(
                btn_frame,
                text="我已完成登入",
                command=on_complete,
                width=15
            )
            complete_btn.pack(side=tk.LEFT, padx=5)

            cancel_btn = ttk.Button(
                btn_frame,
                text="取消",
                command=on_cancel,
                width=15
            )
            cancel_btn.pack(side=tk.LEFT, padx=5)

            # Make dialog modal
            dialog.grab_set()
            parent_window.wait_window(dialog)

            return result['completed']
        else:
            # Console mode
            print("\n🔞 需要年齡驗證")
            print("瀏覽器已開啟！")
            print("\n請完成以下步驟：")
            print("1. 登入您的 YouTube 帳號")
            print("2. 播放影片以通過年齡驗證")
            print("3. 完成後按 Enter 繼續...")
            input()
            return True