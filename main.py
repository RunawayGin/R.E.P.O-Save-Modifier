#!/usr/bin/env python3
"""
Repo Save Modifier - Main entry point

A desktop application for editing Repo game save files.
"""

import sys
import os
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from app.ui.main_window import MainWindow
from app import __version__

def excepthook(exc_type, exc_value, exc_tb):
    """
    Global exception handler to show unhandled exceptions in a message box
    """
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    QMessageBox.critical(
        None, 
        "Unexpected Error",
        f"An unexpected error occurred:\n\n{tb}\n\nPlease report this issue."
    )
    sys.exit(1)

def main():
    """Main application entry point"""
    # Set the working directory to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Set the exception hook
    sys.excepthook = excepthook
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Repo Save Modifier")
    app.setApplicationVersion(__version__)
    
    # High DPI settings
    if hasattr(QApplication, "setHighDpiScaleFactorRoundingPolicy"):
        # Use newer method if available (Qt 6.0+)
        from PySide6.QtCore import Qt
        app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    else:
        # Fall back to older methods
        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()