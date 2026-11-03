"""
GestureOS — Desktop Application Entry Point
"""
import sys
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from utils.logging_config import logger
from utils.model_downloader import ensure_model_downloaded


def main():
    logger.info("Checking MediaPipe model assets...")
    ensure_model_downloaded()

    logger.info("Launching GestureOS...")
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    exit_code = app.exec()
    logger.info(f"GestureOS terminated with exit code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

    