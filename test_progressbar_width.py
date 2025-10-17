#!/usr/bin/env python3
"""
Test different methods to make tkinter progress bar wider
"""

import tkinter as tk
from tkinter import ttk

def test_progressbar_methods():
    root = tk.Tk()
    root.title("Progress Bar Width Test")
    root.geometry("600x400")

    # Method 1: Using style configuration with thickness
    print("Testing Method 1: Style thickness")
    frame1 = ttk.Frame(root)
    frame1.pack(side=tk.LEFT, padx=20, pady=20)
    ttk.Label(frame1, text="Method 1: Style thickness=50").pack()

    style1 = ttk.Style()
    style1.configure("Thick1.Vertical.TProgressbar", thickness=50)
    pb1 = ttk.Progressbar(frame1, mode='determinate', orient='vertical',
                         length=300, style="Thick1.Vertical.TProgressbar")
    pb1.pack(pady=10)
    pb1['value'] = 50

    # Method 2: Using ipadx/ipady on the container
    print("Testing Method 2: Container padding")
    frame2 = ttk.Frame(root)
    frame2.pack(side=tk.LEFT, padx=20, pady=20)
    ttk.Label(frame2, text="Method 2: Container ipadx=20").pack()

    container2 = tk.Frame(frame2, bg='lightgray')
    container2.pack(pady=10, ipadx=20, ipady=5)

    pb2 = ttk.Progressbar(container2, mode='determinate', orient='vertical', length=300)
    pb2.pack()
    pb2['value'] = 50

    # Method 3: Using Canvas to create custom progress bar
    print("Testing Method 3: Custom Canvas progress bar")
    frame3 = ttk.Frame(root)
    frame3.pack(side=tk.LEFT, padx=20, pady=20)
    ttk.Label(frame3, text="Method 3: Canvas 40px wide").pack()

    canvas = tk.Canvas(frame3, width=40, height=300, bg='#E0E0E0', bd=1, relief='sunken')
    canvas.pack(pady=10)

    # Draw progress
    progress_height = int(300 * 0.5)  # 50% progress
    canvas.create_rectangle(0, 300 - progress_height, 40, 300, fill='#2E8B57', outline='')

    # Method 4: Frame-based progress bar
    print("Testing Method 4: Frame-based progress bar")
    frame4 = ttk.Frame(root)
    frame4.pack(side=tk.LEFT, padx=20, pady=20)
    ttk.Label(frame4, text="Method 4: Frame 30px wide").pack()

    progress_container = tk.Frame(frame4, width=30, height=300, bg='#E0E0E0', relief='sunken', bd=1)
    progress_container.pack(pady=10)
    progress_container.pack_propagate(False)  # Maintain fixed size

    progress_fill = tk.Frame(progress_container, bg='#2E8B57')
    progress_fill.place(x=0, rely=0.5, relwidth=1, relheight=0.5)  # 50% progress

    # Method 5: Style with different approach
    print("Testing Method 5: Style with troughrelief")
    frame5 = ttk.Frame(root)
    frame5.pack(side=tk.LEFT, padx=20, pady=20)
    ttk.Label(frame5, text="Method 5: Style comprehensive").pack()

    style5 = ttk.Style()
    style5.configure("Thick5.Vertical.TProgressbar",
                    thickness=35,
                    troughcolor='#E0E0E0',
                    background='#2E8B57',
                    borderwidth=2,
                    relief='solid')

    pb5 = ttk.Progressbar(frame5, mode='determinate', orient='vertical',
                         length=300, style="Thick5.Vertical.TProgressbar")
    pb5.pack(pady=10)
    pb5['value'] = 50

    root.mainloop()

if __name__ == "__main__":
    test_progressbar_methods()