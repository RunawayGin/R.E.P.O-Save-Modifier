import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QLabel, QPushButton, QMessageBox, QFileDialog,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QSize, QPoint, Signal, Slot, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QPixmap

from .pages import HomePage, PlayerPage, ItemsPage, GameStatsPage
from .widgets import ModernButton
from .themes import ThemeManager
from ..core import SaveManager, GameSave, SteamAPI, Settings
from ..utils import generate_all_icons

# Constants
WINDOW_SIZE = (1200, 720)  # (Width, Height)
WINDOW_MINIMUM_SIZE = (960, 540)  # Minimum window size
LEFT_MENU_WIDTH_EXPANDED = 200     # Width when sidebar is expanded
LEFT_MENU_WIDTH_COLLAPSED = 80     # Width when sidebar is collapsed
TITLE_BAR_HEIGHT = 50              # Height of title bar
TITLE_BUTTON_SIZE = 45             # Size of buttons in title bar
SIDEBAR_BUTTON_HEIGHT = 50         # Height of sidebar buttons

class MainWindow(QMainWindow):
    """
    Main application window for Repo Save Modifier
    """
    
    def __init__(self):
        """Initialize the main window"""
        super().__init__()
        
        # Initialize core components
        self.settings = Settings()
        self.theme_manager = ThemeManager(self.settings)
        self.save_manager = SaveManager()
        self.steam_api = SteamAPI()
        
        # Initialize user cache
        from ..core.user_cache import UserCache
        self.user_cache = UserCache()
        
        # Current save data
        self.current_save_path = None
        self.game_save = None
        self.original_data = None  # For reverting changes
        
        # Flag to track if a save is loaded
        self.is_save_loaded = False
        
        # Get app base directory for resources
        self.app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.icons_dir = os.path.join(self.app_dir, 'resources', 'icons')
        
        # Ensure icons exist
        self.ensure_icons_exist()
        
        # Setup window properties
        self.setWindowTitle("Repo Save Modifier")
        self.setWindowIcon(QIcon(os.path.join(self.icons_dir, "home.svg")))
        self.resize(*WINDOW_SIZE)
        self.setMinimumSize(*WINDOW_MINIMUM_SIZE)
        
        # Remove standard title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Setup UI
        self.setup_ui()
        
        # Apply theme
        self.theme_manager.apply_theme(self)
        
        # Connect signals
        self.setup_connections()
        
        # For window dragging
        self.drag_pos = None
        
        # Sidebar toggle state
        self.is_sidebar_expanded = True
        
        # Start at home page
        self.set_page(0)
    
    def setup_ui(self):
        """Set up the UI components"""
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create custom title bar
        self.create_title_bar()
        
        # Content area (sidebar + main content)
        self.content_area = QHBoxLayout()
        self.content_area.setContentsMargins(0, 0, 0, 0)
        self.content_area.setSpacing(0)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Add content area to main layout
        self.main_layout.addLayout(self.content_area)
        
        # After creating player_page, set the references
        self.player_page.set_steam_api(self.steam_api)
        self.player_page.user_cache = self.user_cache  # Share the user cache instance
    
    def create_title_bar(self):
        """Create the custom title bar"""
        # Title bar frame
        self.title_bar = QFrame()
        self.title_bar.setMaximumHeight(TITLE_BAR_HEIGHT)
        self.title_bar.setMinimumHeight(TITLE_BAR_HEIGHT)
        self.title_bar.setObjectName("title_bar")
        
        # Title bar layout
        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(10, 0, 10, 0)
        self.title_bar_layout.setSpacing(0)
        
        # Menu toggle button - adjust position to align with sidebar icons
        self.btn_toggle_menu = QPushButton()
        self.btn_toggle_menu.setToolTip("Toggle Menu")
        self.btn_toggle_menu.setIcon(QIcon(os.path.join(self.icons_dir, "menu.svg")))
        self.btn_toggle_menu.setIconSize(QSize(24, 24))
        self.btn_toggle_menu.setFixedSize(TITLE_BUTTON_SIZE, TITLE_BUTTON_SIZE)
        self.btn_toggle_menu.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_menu.setObjectName("btn_toggle_menu")
        
        # Add left margin to align with sidebar properly
        left_margin_spacer = QSpacerItem(10, 1, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.title_bar_layout.addItem(left_margin_spacer)
        
        # Now add the toggle button with proper alignment
        self.title_bar_layout.addWidget(self.btn_toggle_menu)
        
        # Add spacing between burger menu and logo
        menu_logo_spacer = QSpacerItem(15, 1, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.title_bar_layout.addItem(menu_logo_spacer)
        
        # Logo label (use SVG for better quality)
        self.logo_label = QLabel()
        logo_path = os.path.join(self.icons_dir, "reposavelogo.svg")  # Changed to SVG
        
        if os.path.exists(logo_path):
            # Use QSvgWidget for better SVG rendering if available
            try:
                from PySide6.QtSvg import QSvgWidget
                
                # Remove the QLabel
                self.logo_label.deleteLater()
                
                # Create SVG widget instead
                self.logo_widget = QSvgWidget(logo_path)
                scaled_height = TITLE_BAR_HEIGHT - 14  # Leave some margin
                self.logo_widget.setFixedHeight(scaled_height)
                # Calculate proportional width
                self.logo_widget.setFixedWidth(scaled_height * 4)  # Adjust multiplier to match your SVG aspect ratio
                
                # Add SVG widget to layout
                self.title_bar_layout.addWidget(self.logo_widget)
                
            except ImportError:
                # Fallback to QIcon if QSvgWidget is not available
                logo_icon = QIcon(logo_path)
                self.logo_label.setPixmap(logo_icon.pixmap(QSize(TITLE_BAR_HEIGHT * 4, TITLE_BAR_HEIGHT - 14)))
                self.title_bar_layout.addWidget(self.logo_label)
        else:
            # Fallback to text if SVG doesn't exist
            self.logo_label.setText("Repo Save Modifier")
            self.logo_label.setStyleSheet(f"""
                font-size: 12pt;
                font-weight: bold;
                color: #dce1ec;
            """)
            self.title_bar_layout.addWidget(self.logo_label)
        
        self.title_bar_layout.addStretch()
        
        # Right-side buttons
        self.btn_minimize = QPushButton()
        self.btn_minimize.setToolTip("Minimize")
        self.btn_minimize.setIcon(QIcon(os.path.join(self.icons_dir, "minimize.svg")))
        self.btn_minimize.setIconSize(QSize(16, 16))
        self.btn_minimize.setFixedSize(TITLE_BUTTON_SIZE, TITLE_BUTTON_SIZE)
        self.btn_minimize.setCursor(Qt.PointingHandCursor)
        
        self.btn_maximize = QPushButton()
        self.btn_maximize.setToolTip("Maximize")
        self.btn_maximize.setIcon(QIcon(os.path.join(self.icons_dir, "maximize.svg")))
        self.btn_maximize.setIconSize(QSize(16, 16))
        self.btn_maximize.setFixedSize(TITLE_BUTTON_SIZE, TITLE_BUTTON_SIZE)
        self.btn_maximize.setCursor(Qt.PointingHandCursor)
        
        self.btn_close = QPushButton()
        self.btn_close.setToolTip("Close")
        self.btn_close.setIcon(QIcon(os.path.join(self.icons_dir, "close.svg")))
        self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close.setFixedSize(TITLE_BUTTON_SIZE, TITLE_BUTTON_SIZE)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        
        # Add widgets to title bar
        self.title_bar_layout.addWidget(self.btn_minimize)
        self.title_bar_layout.addWidget(self.btn_maximize)
        self.title_bar_layout.addWidget(self.btn_close)
        
        # Add title bar to main layout
        self.main_layout.addWidget(self.title_bar)
    

    def create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        # Sidebar frame
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(LEFT_MENU_WIDTH_EXPANDED)
        self.sidebar.setMaximumWidth(LEFT_MENU_WIDTH_EXPANDED)
        
        # Set sidebar background color using theme manager
        self.sidebar.setStyleSheet(f"""
            #sidebar {{
                background-color: {self.theme_manager.get_color("COLOR_SIDEBAR_BG")};
                border-right: 1px solid {self.theme_manager.get_color("COLOR_DARK_THREE")};
            }}
        """)
        
        # Sidebar layout - adjust margins to align with burger menu in title bar
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 15, 15, 15)  # Increased left margin to match burger button
        self.sidebar_layout.setSpacing(8)  # Increased for better visual spacing
        
        # Create navigation buttons
        self.btn_home = self.create_sidebar_button("Home", os.path.join(self.icons_dir, "home.svg"), True)
        self.btn_game_stats = self.create_sidebar_button("Game Stats", os.path.join(self.icons_dir, "stats.svg"))
        self.btn_player = self.create_sidebar_button("Player Stats", os.path.join(self.icons_dir, "player.svg"))
        self.btn_items = self.create_sidebar_button("Items", os.path.join(self.icons_dir, "items.svg"))
        
        
        # Add separator
        self.sidebar_layout.addSpacing(10)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #343b48;")
        self.sidebar_layout.addWidget(separator)
        
        self.sidebar_layout.addSpacing(10)
        
        # File operations buttons
        self.btn_save = self.create_sidebar_button("Save Changes", os.path.join(self.icons_dir, "save_file.svg"))
        
        # Add buttons to layout
        self.sidebar_layout.addWidget(self.btn_home)
        self.sidebar_layout.addWidget(self.btn_game_stats)
        self.sidebar_layout.addWidget(self.btn_player)
        self.sidebar_layout.addWidget(self.btn_items)
        self.sidebar_layout.addWidget(self.btn_save)
        
        # Add spacer at the bottom
        self.sidebar_layout.addStretch()
        
        # Add settings button at the bottom
        self.btn_settings = self.create_sidebar_button("Settings", os.path.join(self.icons_dir, "settings.svg"))
        self.sidebar_layout.addWidget(self.btn_settings)
        
        # Add attribution label
        attribution_label = QLabel("Made by: Runaway_Gin")
        attribution_label.setStyleSheet(f"""
            color: {self.theme_manager.get_color("COLOR_TEXT_FOREGROUND")};
            font-size: 9pt;
            padding: 4px;
            margin-top: 4px;
        """)
        attribution_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(attribution_label)
        
        # Add sidebar to content area
        self.content_area.addWidget(self.sidebar)
    
    def create_sidebar_button(self, text, icon_path, is_active=False):
        """
        Create a sidebar button
        
        Args:
            text (str): Button text
            icon_path (str): Path to icon
            is_active (bool, optional): Whether button is active. Defaults to False.
            
        Returns:
            QPushButton: Sidebar button
        """
        btn = QPushButton(text)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(24, 24))
        btn.setMinimumHeight(SIDEBAR_BUTTON_HEIGHT)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        
        # Set object name for styling
        btn.setObjectName("sidebar_button")
        
        # Apply styling based on active state
        if is_active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme_manager.get_color("COLOR_BLUE_ONE")};
                    color: {self.theme_manager.get_color("COLOR_TEXT_ACTIVE")};
                    border: none;
                    border-radius: 5px;
                    text-align: left;
                    padding-left: 15px;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.theme_manager.get_color("COLOR_TEXT_FOREGROUND")};
                    border: none;
                    border-radius: 5px;
                    text-align: left;
                    padding-left: 15px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme_manager.get_color("COLOR_DARK_FOUR")};
                    color: {self.theme_manager.get_color("COLOR_TEXT_ACTIVE")};
                }}
            """)
    
        return btn
    
    def create_main_content(self):
        """Create the main content area"""
        # Main content frame
        self.main_content = QFrame()
        self.main_content.setObjectName("main_content")
        
        # Main content layout
        self.main_content_layout = QVBoxLayout(self.main_content)
        self.main_content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_content_layout.setSpacing(0)
        
        # Create stacked widget for pages
        self.pages = QStackedWidget()
        
        # Create pages
        self.home_page = HomePage()
        self.player_page = PlayerPage()
        self.items_page = ItemsPage()
        self.game_stats_page = GameStatsPage()
        
        # Add pages to stack
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.player_page)
        self.pages.addWidget(self.items_page)
        self.pages.addWidget(self.game_stats_page)
        
        # Add pages widget to main content
        self.main_content_layout.addWidget(self.pages)
        
        # Add main content to content area
        self.content_area.addWidget(self.main_content)
    
    def setup_connections(self):
        """Connect signals to slots"""
        # Title bar buttons
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_maximize.clicked.connect(self.toggle_maximize)
        self.btn_close.clicked.connect(self.close)
        self.btn_toggle_menu.clicked.connect(self.toggle_sidebar)
        
        # Sidebar buttons
        self.btn_home.clicked.connect(lambda: self.set_page(0))
        self.btn_game_stats.clicked.connect(lambda: self.set_page(3))  # Changed order
        self.btn_player.clicked.connect(lambda: self.set_page(1))
        self.btn_items.clicked.connect(lambda: self.set_page(2))
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_settings.clicked.connect(self.show_settings)
        
        # Page signals
        self.home_page.save_selected.connect(self.load_save_file)
        self.home_page.refresh_button.clicked.connect(self.refresh_save_list)
        self.home_page.new_game_requested.connect(self.create_new_game_save)
        
        # Player page signals
        self.player_page.data_changed.connect(self.mark_as_modified)
        self.player_page.add_player_requested.connect(self.add_player)
        
        # Game stats page signals
        self.game_stats_page.data_changed.connect(self.mark_as_modified)
        
        # Items page signals
        self.items_page.item_purchased_changed.connect(self.on_item_purchased_changed)
        self.items_page.item_upgrade_changed.connect(self.on_item_upgrade_changed)
        
        # Steam API signals
        self.steam_api.avatar_fetched.connect(self.on_avatar_fetched)
        
        # Load save files on startup
        QTimer.singleShot(100, self.refresh_save_list)

        

    def set_page(self, index):
        """
        Set the current page
        
        Args:
            index (int): Page index
        """
        # Update sidebar buttons
        buttons = [self.btn_home, self.btn_player, self.btn_items, self.btn_game_stats]
        
        # Reset all buttons
        for i, btn in enumerate(buttons):
            btn.setChecked(False)
            
            # Update styling directly instead of using objectName
            if i == index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.theme_manager.get_color("COLOR_BLUE_ONE")};
                        color: {self.theme_manager.get_color("COLOR_TEXT_ACTIVE")};
                        border: none;
                        border-radius: 5px;
                        text-align: left;
                        padding-left: 15px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {self.theme_manager.get_color("COLOR_TEXT_FOREGROUND")};
                        border: none;
                        border-radius: 5px;
                        text-align: left;
                        padding-left: 15px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.theme_manager.get_color("COLOR_DARK_FOUR")};
                        color: {self.theme_manager.get_color("COLOR_TEXT_ACTIVE")};
                    }}
                """)
        
        # Set active button
        if 0 <= index < len(buttons):
            buttons[index].setChecked(True)
        
        # Set page
        self.pages.setCurrentIndex(index)
        
        # Update window title
        page_names = ["Home", "Game Stats", "Player Stats", "Items"]
        if 0 <= index < len(page_names):
            self.setWindowTitle(f"Repo Save Modifier - {page_names[index]}")
    
    def toggle_sidebar(self):
        """Toggle the sidebar expanded/collapsed state"""
        width = LEFT_MENU_WIDTH_COLLAPSED if self.is_sidebar_expanded else LEFT_MENU_WIDTH_EXPANDED
        
        # Create animation
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_animation.setDuration(250)
        self.sidebar_animation.setStartValue(self.sidebar.width())
        self.sidebar_animation.setEndValue(width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        # Create animation for maximum width as well
        self.sidebar_animation2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_animation2.setDuration(250)
        self.sidebar_animation2.setStartValue(self.sidebar.width())
        self.sidebar_animation2.setEndValue(width)
        self.sidebar_animation2.setEasingCurve(QEasingCurve.InOutQuart)
        
        # Start animations
        self.sidebar_animation.start()
        self.sidebar_animation2.start()
        
        # Update toggle state
        self.is_sidebar_expanded = not self.is_sidebar_expanded
        
        # Update button tooltips
        if self.is_sidebar_expanded:
            self.btn_toggle_menu.setToolTip("Collapse Menu")
        else:
            self.btn_toggle_menu.setToolTip("Expand Menu")
    
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
            self.btn_maximize.setIcon(QIcon(os.path.join(self.icons_dir, "maximize.svg")))
            self.btn_maximize.setToolTip("Maximize")
        else:
            self.showMaximized()
            self.btn_maximize.setIcon(QIcon(os.path.join(self.icons_dir, "restore.svg")))
            self.btn_maximize.setToolTip("Restore")
    
    def load_save_file(self, file_path):
        """
        Load a save file
        
        Args:
            file_path (str): Path to the save file
        """
        try:
            # Load JSON data from ES3 file
            print(f"Loading save file: {file_path}")
            raw_data = self.save_manager.load_json_from_es3(file_path)
            
            if raw_data is None:
                QMessageBox.critical(self, "Error", "Failed to load save file. The file may be corrupted or in an unsupported format.")
                return
            
            # Store original data for reverting changes
            self.original_data = raw_data
            
            # Create game save model
            self.game_save = GameSave(raw_data)
            self.is_save_loaded = True
            
            # Store current path
            self.current_save_path = file_path
            
            # Add to recent files
            self.settings.add_recent_file(file_path)
            
            # Update UI with save data
            self.update_ui_with_save_data()
            
            # Make sure player page knows a save is loaded
            self.player_page.set_save_loaded_state(True)
            self.player_page.set_steam_api(self.steam_api)
            print(f"Set player page save loaded state to True")
            
            # Add players to user cache and start fetching avatars one by one with a small delay
            player_ids = list(self.game_save.players.keys())
            for index, player_id in enumerate(player_ids):
                player_data = self.game_save.players[player_id]
                
                # Add to user cache first
                avatar_path = self.steam_api.get_cached_avatar_path(player_id)
                self.user_cache.add_user(player_id, player_data.name, avatar_path)
                
                # Use cached avatar immediately if available
                if avatar_path:
                    print(f"Setting cached avatar for {player_id}")
                    self.player_page.update_player_avatars(player_id, avatar_path)
                
                # Schedule avatar fetch with a delay to avoid overwhelming the API
                # This way avatars are fetched one after another with a small delay
                QTimer.singleShot(index * 300, lambda pid=player_id: self.steam_api.fetch_avatar_async(pid))
            
            # Navigate to game stats page
            self.set_page(3)
            
            # Show success message
            QMessageBox.information(self, "Success", "Save file loaded successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the save file: {str(e)}")
    
    
    def update_ui_with_save_data(self):
        """Update UI components with save data"""
        if self.game_save:
            print("Updating UI with save data")
            
            # Clear existing player cards first to ensure complete refresh
            self.player_page.clear_cards()
            
            # Update player page with all players
            self.player_page.display_players(self.game_save.players, self.game_save)
            
            # Re-apply avatars immediately for all players who have cached avatars
            for player_id in self.game_save.players:
                avatar_path = self.steam_api.get_cached_avatar_path(player_id)
                if avatar_path:
                    print(f"Re-applying cached avatar for {player_id}")
                    self.player_page.update_player_avatars(player_id, avatar_path)
            
            # Update items page
            self.items_page.display_items(self.game_save.items)
            self.items_page.display_upgrades(self.game_save.items)
            
            # Update game stats page
            self.game_stats_page.display_game_save(self.game_save)
            
            print("UI update complete")
    
    
    def open_save_file(self):
        """Open a save file dialog"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Repo Save Files (*.Es3)")
        
        # Start in the default save folder
        if self.save_manager.default_save_path and os.path.exists(self.save_manager.default_save_path):
            file_dialog.setDirectory(self.save_manager.default_save_path)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.load_save_file(selected_files[0])
    
    def save_changes(self):
        """Save changes to the save file"""
        if not self.current_save_path or not self.game_save:
            QMessageBox.warning(self, "Warning", "No save file loaded.")
            return
        
        try:
            print("==== STARTING SAVE PROCESS ====")
            
            # Explicitly pull ALL data from UI widgets before saving
            
            # 1. Update team name from game stats page
            self.game_save.team_name = self.game_stats_page.get_team_name()
            print(f"Team name set to: {self.game_save.team_name}")
            
            # 2. Update all player data from player cards
            for player_id, card in self.player_page.player_cards.items():
                if player_id in self.game_save.players:
                    player = self.game_save.players[player_id]
                    
                    print(f"\nProcessing player {player_id}, name: {player.name}")
                    
                    # Update health value
                    player.health = card.health
                    player.max_health = card.max_health
                    print(f"  Health: {player.health}/{player.max_health}")
                    
                    # IMPORTANT: Get ALL upgrades at once using the new method
                    all_upgrades = card.upgrades  # Direct access to the upgrades dictionary
                    print(f"  All upgrades from card: {all_upgrades}")
                    
                    # Update each upgrade in the player data
                    for upgrade_type, value in all_upgrades.items():
                        old_value = player.upgrades.get(upgrade_type, "not set")
                        player.upgrades[upgrade_type] = value
                        print(f"  Upgrading {upgrade_type}: {old_value} -> {value}")
            
            # 3. Update all items data from items page
            print("\nProcessing items:")
            # Regular items
            for item_name, editor in self.items_page.item_editors.items():
                quantity = editor.get_value()
                old_quantity = self.game_save.items["purchased"].get(item_name, "not set")
                self.game_save.update_item_purchased(item_name, quantity)
                print(f"  Item {item_name}: {old_quantity} -> {quantity}")
            
            # Item upgrades
            print("\nProcessing item upgrades:")
            for item_name, editor in self.items_page.upgrade_editors.items():
                quantity = editor.get_value()
                old_quantity = self.game_save.items["upgradesPurchased"].get(item_name, "not set")
                self.game_save.update_upgrade_purchased(item_name, quantity)
                print(f"  Item Upgrade {item_name}: {old_quantity} -> {quantity}")
            
            # Now create the updated data with ALL the changes
            print("\nCreating updated data with all changes...")
            updated_data = self.game_save.update_data(self.original_data.copy())
            
            # Save to file with debug information to show differences
            print("\nSaving to file...")
            success = self.save_manager.save_es3_from_json(
                updated_data, 
                self.current_save_path,
                debug_compare=True,
                debug_player_stats=True
            )
            
            if success:
                # Update window title to remove modified indicator
                if self.windowTitle().endswith("*"):
                    self.setWindowTitle(self.windowTitle()[:-2])
                    
                print("Save successful!")
                QMessageBox.information(self, "Success", "Save file updated successfully!")
            else:
                print("Save failed!")
                QMessageBox.critical(self, "Error", "Failed to save changes.")
            
            print("==== SAVE PROCESS COMPLETED ====")
                    
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR during save: {error_details}")
            QMessageBox.critical(self, "Error", f"An error occurred while saving changes:\n\n{str(e)}\n\nDetails:\n{error_details}")
    
    def mark_as_modified(self):
        """Mark the save file as modified"""
        # Update window title to show modified status
        if not self.windowTitle().endswith("*"):
            self.setWindowTitle(f"{self.windowTitle()} *")
    
    def add_player(self, player_id, player_name):
        """
        Add a new player to the current save
        
        Args:
            player_id (str): Steam ID of the player
            player_name (str): Name of the player from Steam
        """
        print(f"MainWindow: Adding player {player_id} with name '{player_name}'")
        
        # Verify valid name
        if not player_name or player_name.strip() == "":
            player_name = f"Player_{player_id[-4:]}"
            print(f"Empty player name detected, using fallback: {player_name}")
        
        # Count current players
        current_player_count = len(self.game_save.players)
        
        if current_player_count >= 6:
            QMessageBox.warning(self, "Warning", "Maximum number of players (6) already reached.")
            return
            
        # Check if player already exists
        if player_id in self.game_save.players:
            QMessageBox.warning(self, "Warning", "Player with this Steam ID already exists in the save.")
            return
            
        try:
            # Add player to game save
            new_player = self.game_save.add_player(player_id, player_name)
            
            # Debug verification
            print(f"New player added: {player_id}, name: '{new_player.name}'")
            
            # Update original data
            self.original_data = self.game_save.raw_data
            
            # CRITICAL: Force complete UI refresh by clearing all cards first
            # and then redisplaying all players
            self.player_page.clear_cards()
            self.player_page.display_players(self.game_save.players, self.game_save)
            
            # Apply all cached avatars immediately
            for pid in self.game_save.players:
                avatar_path = self.steam_api.get_cached_avatar_path(pid)
                if avatar_path:
                    print(f"Applying cached avatar for {pid}")
                    self.player_page.update_player_avatars(pid, avatar_path)
            
            # Update other UI components
            self.items_page.display_items(self.game_save.items)
            self.items_page.display_upgrades(self.game_save.items)
            self.game_stats_page.display_game_save(self.game_save)
            
            # Mark as modified
            self.mark_as_modified()
            
            # Check for cached avatar for newly added player
            avatar_path = self.steam_api.get_cached_avatar_path(player_id)
            if avatar_path:
                print(f"Using cached avatar for {player_id}: {avatar_path}")
                # Update avatar immediately if already cached
                self.player_page.update_player_avatars(player_id, avatar_path)
            
            # Then fetch/update avatar asynchronously
            print(f"Fetching avatar asynchronously for {player_id}")
            self.steam_api.fetch_avatar_async(player_id)
            
            # Add to user cache
            self.user_cache.add_user(player_id, player_name, avatar_path)
            
            # Show success message
            QMessageBox.information(self, "Success", f"Player added:\nName: {player_name}\nSteam ID: {player_id}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add player: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_upgrade_changed(self, player_id, upgrade_type, value):
        """
        Handle when a player upgrade changes
        
        Args:
            player_id (str): Player ID
            upgrade_type (str): Upgrade type
            value (int): New value
        """
        if self.game_save and player_id in self.game_save.players:
            # Update player data
            self.game_save.players[player_id].upgrades[upgrade_type] = value
            
            # If health upgrade changed, update max health
            if upgrade_type == "health":
                player = self.game_save.players[player_id]
                player.max_health = 100 + (value * 20)
                
                # Update health display in player page
                self.player_page.update_player_health(player_id, player.health, player.max_health)
            
            # Mark as modified
            self.mark_as_modified()
    
    def on_item_purchased_changed(self, item_name, quantity):
        """
        Handle when an item purchase quantity changes
        
        Args:
            item_name (str): Item name
            quantity (int): New quantity
        """
        if self.game_save:
            # Update item in game save
            self.game_save.update_item_purchased(item_name, quantity)
            
            # Mark as modified
            self.mark_as_modified()
    
    def on_item_upgrade_changed(self, item_name, quantity):
        """
        Handle when an item upgrade quantity changes
        
        Args:
            item_name (str): Item name
            quantity (int): New quantity
        """
        if self.game_save:
            # Update upgrade in game save
            self.game_save.update_upgrade_purchased(item_name, quantity)
            
            # Mark as modified
            self.mark_as_modified()
    
    def on_avatar_fetched(self, player_id, image_path):
        """
        Handle when a player avatar is fetched
        
        Args:
            player_id (str): Player ID
            image_path (str): Path to avatar image
        """
        # Update avatar in player page
        self.player_page.update_player_avatars(player_id, image_path)
    
    def create_new_game_save(self):
        """Create a new game save from scratch"""
        try:
            from PySide6.QtWidgets import QInputDialog, QMessageBox
            
            # Ask for team name
            team_name, ok = QInputDialog.getText(self, "New Game", "Enter team name:", text="R.E.P.O. Team")
            
            if not ok:
                return  # User cancelled
            
            # Create new game save via the SaveManager
            save_folder, file_path, game_save = self.save_manager.create_new_game_save(team_name)
            
            if not file_path:
                QMessageBox.critical(self, "Error", "Failed to create new game save.")
                return
            
            # Load the new save
            self.load_save_file(file_path)
            
            # Explicitly set player page save loaded state again
            self.player_page.set_save_loaded_state(True)
            
            # Show success message
            QMessageBox.information(self, "Success", f"New game created:\nTeam: {team_name}\nFile: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new game: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_settings(self):
        """Show the settings dialog"""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented.")
        
    def ensure_icons_exist(self):
        """Ensure that all required icons exist"""
        # Get the application's base directory
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        icons_dir = os.path.join(app_dir, 'resources', 'icons')
        
        # Check if at least one icon exists
        if not os.path.exists(os.path.join(icons_dir, 'home.svg')):
            # Create resources directory if needed
            os.makedirs(icons_dir, exist_ok=True)
            
            # Generate all icons
            from ..utils import generate_all_icons
            generate_all_icons(icons_dir)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        # Enable window dragging from title bar
        if event.button() == Qt.LeftButton and self.title_bar.rect().contains(event.pos()):
            self.drag_pos = event.globalPos()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        # Move window when dragged from title bar
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            if self.isMaximized():
                # Restore before moving if maximized
                self.showNormal()
                # Update button icon
                self.btn_maximize.setIcon(QIcon(os.path.join(self.icons_dir, "maximize.svg")))
                self.btn_maximize.setToolTip("Maximize")
            
            # Calculate new position
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        # Reset drag position
        self.drag_pos = None
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Check for unsaved changes
        if self.windowTitle().endswith("*"):
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_changes()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
                return
        
        # Cleanup threads
        if hasattr(self, 'steam_api'):
            self.steam_api.cleanup()
        
        event.accept()
    
    def refresh_save_list(self):
        """Refresh the list of save files"""
        try:
            # Get the default save folder
            save_folder = self.save_manager.default_save_path
            print(f"Refreshing save list from: {save_folder}")
            
            # List save files
            save_files = self.save_manager.list_save_files(save_folder)
            print(f"Found {len(save_files)} save files")
            
            # Update the home page with the list
            self.home_page.populate_save_list(save_files)
            
        except Exception as e:
            print(f"Exception during refresh: {str(e)}")
            QMessageBox.warning(
                self, 
                "Error", 
                f"Failed to refresh save files list: {str(e)}"
            )