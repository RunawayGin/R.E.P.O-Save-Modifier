from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QCursor

class ModernButton(QPushButton):
    """
    Custom button with modern styling, supporting different sizes and themes
    """
    
    def __init__(self, text="", size="medium", icon=None, is_active=False, accent_color=None):
        """
        Initialize the modern button
        
        Args:
            text (str, optional): Button text. Defaults to "".
            size (str, optional): Button size ("small", "medium", "large"). Defaults to "medium".
            icon (str, optional): Icon path. Defaults to None.
            is_active (bool, optional): Whether the button is active/selected. Defaults to False.
            accent_color (str, optional): Button accent color. Defaults to None.
        """
        super().__init__(text)
        
        # Set cursor
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Set icon if provided
        if icon:
            self.setIcon(QIcon(icon))
            icon_size = 16
            if size == "large":
                icon_size = 24
            elif size == "small":
                icon_size = 12
            self.setIconSize(QSize(icon_size, icon_size))
        
        # Set active state
        self.is_active = is_active
        self.accent_color = accent_color or "#568af2"  # Default blue accent
        
        # Apply style based on size
        self._apply_style(size)
    
    def _apply_style(self, size):
        """
        Apply style based on size
        
        Args:
            size (str): Button size ("small", "medium", "large")
        """
        # Color settings - Using consistent variables
        bg_color = "#2c313c"
        bg_hover = "#343b48"
        text_color = "#8a95aa"
        text_hover = "#dce1ec"
        active_color = self.accent_color
        
        # Size settings - More consistent dimensions
        if size == "small":
            padding = "4px 8px"
            border_radius = "4px"
            font_size = "9pt"
        elif size == "medium":
            padding = "6px 12px"
            border_radius = "5px"
            font_size = "10pt"
        elif size == "large":
            padding = "8px 16px"
            border_radius = "6px"
            font_size = "11pt"
        else:
            # Default to medium
            padding = "6px 12px"
            border_radius = "5px"
            font_size = "10pt"
        
        # Different style for active state
        if self.is_active:
            style = f"""
                QPushButton {{
                    background-color: {active_color};
                    color: white;
                    border: none;
                    border-radius: {border_radius};
                    padding: {padding};
                    font-size: {font_size};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {active_color};
                    color: white;
                }}
                QPushButton:pressed {{
                    background-color: {active_color};
                    color: white;
                }}
            """
        else:
            style = f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: none;
                    border-radius: {border_radius};
                    padding: {padding};
                    font-size: {font_size};
                }}
                QPushButton:hover {{
                    background-color: {bg_hover};
                    color: {text_hover};
                }}
                QPushButton:pressed {{
                    background-color: {active_color};
                    color: white;
                }}
            """
        
        self.setStyleSheet(style)
    
    def set_active(self, active):
        """
        Set the button's active state
        
        Args:
            active (bool): Whether the button should be active
        """
        self.is_active = active
        self._apply_style("medium")  # Re-apply current size
    
    def set_accent_color(self, color):
        """
        Set the button's accent color
        
        Args:
            color (str): Hex color code
        """
        self.accent_color = color
        self._apply_style("medium")  # Re-apply current size
