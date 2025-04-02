import os
import json
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor

class ThemeManager(QObject):
    """
    Manages application themes and provides consistent styling
    """
    
    # Signal emitted when theme changes
    theme_changed = Signal(dict)
    
    def __init__(self, settings=None):
        """
        Initialize the theme manager
        
        Args:
            settings: Settings instance for theme persistence
        """
        super().__init__()
        self.settings = settings
        
        # Default font settings
        self.font_family = "Segoe UI"
        
        # Load colors from settings or default to dark theme
        self.colors = self._load_colors()
    
    def _load_colors(self):
        """
        Load colors from settings or default
        
        Returns:
            dict: Theme colors
        """
        # If settings provided, use theme from there
        if self.settings:
            return self.settings.get_theme_colors()
        
        # Otherwise load from colors.json or use hardcoded defaults
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        colors_file = os.path.join(app_dir, 'resources', 'config', 'colors.json')
        
        try:
            # Load colors from file if it exists
            if os.path.exists(colors_file):
                with open(colors_file, 'r', encoding='utf-8') as f:
                    themes = json.load(f)
                return themes.get("dark_theme", self._get_default_colors())
            
            # Otherwise use default
            return self._get_default_colors()
            
        except Exception as e:
            print(f"Error loading theme colors: {str(e)}")
            return self._get_default_colors()
    
    def _get_default_colors(self):
        """
        Get default color theme
        
        Returns:
            dict: Default theme colors
        """
        return {
            "COLOR_DARK_ONE": "#1b1e23",
            "COLOR_DARK_TWO": "#272c36",
            "COLOR_DARK_THREE": "#2c313c",
            "COLOR_DARK_FOUR": "#343b48",
            "COLOR_BLUE_ONE": "#568af2",
            "COLOR_TEXT_FOREGROUND": "#8a95aa",
            "COLOR_TEXT_ACTIVE": "#dce1ec",
            "COLOR_SIDEBAR_BG": "#20242c"
        }
    
    def get_color(self, color_name):
        """
        Get a color from the current theme
        
        Args:
            color_name (str): Color name (e.g., "COLOR_DARK_ONE")
            
        Returns:
            str: Hex color code
        """
        return self.colors.get(color_name, "#000000")
    
    def get_color_obj(self, color_name):
        """
        Get a QColor object from the current theme
        
        Args:
            color_name (str): Color name (e.g., "COLOR_DARK_ONE")
            
        Returns:
            QColor: QColor object
        """
        color_hex = self.get_color(color_name)
        return QColor(color_hex)
    
    def apply_theme(self, widget):
        """
        Apply theme to a widget
        
        Args:
            widget: Widget to apply theme to
        """
        # Main window/application wide stylesheet
        stylesheet = f"""
            /* GLOBAL STYLES */
            QWidget {{
                font-family: "{self.font_family}";
                color: {self.get_color("COLOR_TEXT_FOREGROUND")};
                background-color: {self.get_color("COLOR_DARK_ONE")};
            }}
            
            /* TITLE BAR STYLES */
            #title_bar, #title_container, #btn_toggle_menu,
            #btn_minimize, #btn_maximize, #btn_close {{
                background-color: {self.get_color("COLOR_DARK_THREE")};
            }}
            
            QLabel {{
                color: {self.get_color("COLOR_TEXT_FOREGROUND")};
                background-color: transparent;
            }}
            
            /* BUTTONS */
            QPushButton {{
                background-color: {self.get_color("COLOR_DARK_THREE")};
                border-radius: 5px;
                padding: 5px 10px;
                color: {self.get_color("COLOR_TEXT_FOREGROUND")};
            }}
            
            QPushButton:hover {{
                background-color: {self.get_color("COLOR_DARK_FOUR")};
                color: {self.get_color("COLOR_TEXT_ACTIVE")};
            }}
            
            QPushButton:pressed {{
                background-color: {self.get_color("COLOR_BLUE_ONE")};
                color: {self.get_color("COLOR_TEXT_ACTIVE")};
            }}
            
            /* LEFT MENU BUTTONS */
            #left_menu_button {{
                background-color: transparent;
                border-radius: 8px;
                text-align: left;
                padding-left: 15px;
                color: {self.get_color("COLOR_TEXT_FOREGROUND")};
            }}
            
            #left_menu_button:hover {{
                background-color: {self.get_color("COLOR_DARK_FOUR")};
                color: {self.get_color("COLOR_TEXT_ACTIVE")};
            }}
            
            #left_menu_button_active {{
                background-color: {self.get_color("COLOR_BLUE_ONE")};
                border-radius: 8px;
                text-align: left;
                padding-left: 15px;
                color: {self.get_color("COLOR_TEXT_ACTIVE")};
            }}
            
            /* TABLES */
            QTableView {{
                background-color: {self.get_color("COLOR_DARK_TWO")};
                border: 1px solid {self.get_color("COLOR_DARK_FOUR")};
                border-radius: 5px;
                gridline-color: {self.get_color("COLOR_DARK_FOUR")};
            }}
            
            QTableView::item {{
                padding: 5px;
                border-color: {self.get_color("COLOR_DARK_FOUR")};
            }}
            
            QTableView::item:selected {{
                background-color: {self.get_color("COLOR_BLUE_ONE")};
                color: {self.get_color("COLOR_TEXT_ACTIVE")};
            }}
            
            QHeaderView::section {{
                background-color: {self.get_color("COLOR_DARK_THREE")};
                padding: 5px;
                border: 1px solid {self.get_color("COLOR_DARK_FOUR")};
                color: {self.get_color("COLOR_TEXT_ACTIVE")};
            }}
            
            /* SCROLLBARS */
            QScrollBar:vertical {{
                border: none;
                background-color: {self.get_color("COLOR_DARK_THREE")};
                width: 14px;
                margin: 15px 0 15px 0;
                border-radius: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {self.get_color("COLOR_DARK_FOUR")};
                min-height: 30px;
                border-radius: 7px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {self.get_color("COLOR_BLUE_ONE")};
            }}
            
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
            }}
            
            /* INPUTS */
            QLineEdit, QSpinBox, QComboBox {{
                background-color: {self.get_color("COLOR_DARK_THREE")};
                border: 1px solid {self.get_color("COLOR_DARK_FOUR")};
                border-radius: 5px;
                padding: 5px;
                color: {self.get_color("COLOR_TEXT_FOREGROUND")};
            }}
            
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border: 1px solid {self.get_color("COLOR_BLUE_ONE")};
            }}
        """
        
        widget.setStyleSheet(stylesheet)
    
    def change_theme(self, theme_name):
        """
        Change the current theme
        
        Args:
            theme_name (str): Theme name
        """
        # Save theme to settings if available
        if self.settings:
            self.settings.set("theme", theme_name)
        
        # Reload colors
        self.colors = self._load_colors()
        
        # Emit changed signal
        self.theme_changed.emit(self.colors)
