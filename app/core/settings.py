import os
import json
from PySide6.QtCore import QSettings

class Settings:
    """
    Manages application settings including theme, paths, and user preferences
    """
    
    def __init__(self, app_name="reposavemodifier"):
        """
        Initialize the settings manager
        
        Args:
            app_name (str, optional): Application name for settings storage. Defaults to "reposavemodifier".
        """
        self.app_name = app_name
        
        # QSettings for persistent storage
        self.qsettings = QSettings("RepoSaveModifier", "Settings")
        
        # Default settings
        self.defaults = {
            "theme": "dark_theme",
            "last_save_path": "",
            "recent_files": [],
            "max_recent_files": 5,
            "auto_backup": True,
            "steam_integration": True
        }
        
        # Load settings
        self.settings = self.load_settings()
    
    def load_settings(self):
        """
        Load settings from QSettings
        
        Returns:
            dict: Current settings with defaults applied
        """
        settings = self.defaults.copy()
        
        # Load from QSettings
        for key in settings.keys():
            if self.qsettings.contains(key):
                value_type = type(settings[key])
                
                if value_type == bool:
                    settings[key] = self.qsettings.value(key, settings[key], bool)
                elif value_type == int:
                    settings[key] = self.qsettings.value(key, settings[key], int)
                elif value_type == list:
                    value = self.qsettings.value(key)
                    settings[key] = value if value else settings[key]
                else:
                    settings[key] = self.qsettings.value(key, settings[key])
        
        return settings
    
    def save_settings(self):
        """Save current settings to QSettings"""
        for key, value in self.settings.items():
            self.qsettings.setValue(key, value)
        
        self.qsettings.sync()
    
    def get(self, key, default=None):
        """
        Get a setting value
        
        Args:
            key (str): Setting key
            default (any, optional): Default value if key doesn't exist
            
        Returns:
            any: Setting value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """
        Set a setting value
        
        Args:
            key (str): Setting key
            value (any): Setting value
        """
        self.settings[key] = value
        self.qsettings.setValue(key, value)
        self.qsettings.sync()
    
    def add_recent_file(self, file_path):
        """
        Add a file to recent files list
        
        Args:
            file_path (str): Path to the file
        """
        recent_files = self.settings.get("recent_files", [])
        
        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to front of list
        recent_files.insert(0, file_path)
        
        # Limit the number of entries
        max_files = self.settings.get("max_recent_files", 5)
        recent_files = recent_files[:max_files]
        
        # Update settings
        self.settings["recent_files"] = recent_files
        self.qsettings.setValue("recent_files", recent_files)
        self.qsettings.sync()
    
    def get_theme_colors(self):
        """
        Get colors for the current theme
        
        Returns:
            dict: Theme colors
        """
        theme_name = self.settings.get("theme", "dark_theme")
        
        # Get the application's root directory
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        colors_file = os.path.join(app_dir, 'resources', 'config', 'colors.json')
        
        try:
            # Load colors from file
            if os.path.exists(colors_file):
                with open(colors_file, 'r', encoding='utf-8') as f:
                    themes = json.load(f)
                
                # Return theme colors or default to dark_theme
                return themes.get(theme_name, themes.get("dark_theme", {}))
            else:
                # Default colors if file doesn't exist
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
        except Exception as e:
            print(f"Error loading theme colors: {str(e)}")
            
            # Fallback colors
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
