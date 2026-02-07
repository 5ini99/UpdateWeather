# app/gui.py
import subprocess
import sys
import os
from pathlib import Path

def open_gui():
    script = Path(__file__).parent / "gui_process.py"

    subprocess.Popen(
        [sys.executable, str(script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True  # macOS 关键
    )
