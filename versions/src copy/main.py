import sys
import os

# Ensure project root is in Python's import search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add Chromium flags to reduce memory overhead
sys.argv.extend([
    "--renderer-process-limit=4",          # Cap maximum background renderer processes
    "--process-per-site",                  # Reuse processes for pages on the same domain
    "--js-flags=--expose-gc",              # Enable V8 garbage collection flags
    "--disable-site-isolation-trials",     # Reduces per-tab isolated process overhead
])

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.browser_window import PaleMoonChromiumBrowser


def get_asset_path(filename):
    """Locates assets in both standard Python execution and PyInstaller packages."""
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # Corrected: Points directly to the project root directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'assets', filename)


if __name__ == "__main__":
    # Fix Taskbar Icon grouping on Windows for v1.1.3
    if sys.platform == "win32":
        import ctypes
        myappid = "newmoon.browser.app.1.1.3"  # Updated for v1.1.3
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Required for QStandardPaths to locate persistent storage properly
    QCoreApplication.setOrganizationName("NewMoon")
    QCoreApplication.setApplicationName("NewMoonBrowser")

    app = QApplication(sys.argv)
    
    icon_path = get_asset_path("icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = PaleMoonChromiumBrowser()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
        
    window.show()

    sys.exit(app.exec())