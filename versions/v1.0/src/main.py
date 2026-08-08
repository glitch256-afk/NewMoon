import sys
import os

# Ensure the root project directory is added to sys.path
# so internal imports like "from src.browser_window import ..." work cleanly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.browser_window import PaleMoonChromiumBrowser


def main():
    # Disable sandbox on Linux to prevent startup crashes in restricted environments
    if sys.platform.startswith("linux"):
        os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

    # Set AppUserModelID on Windows so the custom icon appears on the taskbar
    if sys.platform == "win32":
        import ctypes
        myappid = "newmoon.browser.app.1.10"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Load application icon from assets folder
    icon_path = os.path.join(PROJECT_ROOT, "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = PaleMoonChromiumBrowser()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()