from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QSizePolicy, QLineEdit, QScrollArea, QSpacerItem,
    QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..widgets import ModernButton, UserCard

class PlayerPage(QWidget):
    """
    Page for editing player stats
    """
    
    # Signals
    data_changed = Signal()  # Emitted when any data changes
    add_player_requested = Signal(str, str)  # player_id, player_name
    check_save_loaded = Signal()  # Signal to check if a save is loaded
    
    def __init__(self, parent=None):
        """
        Initialize the player page
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Player cards dictionary {player_id: UserCard}
        self.player_cards = {}
        
        # Reference to the steam API for fetching player data
        self.steam_api = None
        
        # Reference to the user cache
        self.user_cache = None
        
        # Flag to track if a save is loaded
        self._save_loaded = False
        
        # Set up UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Page title and button layout
        title_layout = QHBoxLayout()
        
        # Page title
        title = QLabel("Player Editor")
        title.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #dce1ec;
        """)
        title_layout.addWidget(title)
        
        # Add player button
        self.add_player_button = ModernButton("Add Player", "medium")
        self.add_player_button.setStyleSheet("""
            QPushButton {
                background-color: #568af2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3f6fd6;
            }
        """)
        self.add_player_button.clicked.connect(self.on_add_player_clicked)
        title_layout.addStretch()  # Push button to the right
        title_layout.addWidget(self.add_player_button)
        
        main_layout.addLayout(title_layout)
        
        # Create scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: transparent;
                width: 14px;
                margin: 15px 0 15px 0;
                border-radius: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #343b48;
                min-height: 30px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #568af2;
            }
            
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """)
        
        # Create container for scrollable content
        scroll_content = QWidget()
        self.cards_layout = QVBoxLayout(scroll_content)  # Using vertical layout for single column
        self.cards_layout.setContentsMargins(0, 0, 10, 0)
        self.cards_layout.setSpacing(15)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Bottom buttons - save and reset
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.reset_button = ModernButton("Reset Changes", "medium")
        self.reset_button.clicked.connect(self.reset_changes)
        
        buttons_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Initialize empty state
        self.display_empty_state()
    
    def display_empty_state(self):
        """Display empty state when no save is loaded"""
        # Clear existing cards
        self.clear_cards()
        
        # Add empty state message
        empty_label = QLabel("No save file loaded. Please load a save file from the Home page.")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            font-size: 14pt;
            color: #8a95aa;
            padding: 40px;
        """)
        
        # Add to layout
        self.cards_layout.addWidget(empty_label)
    
    def clear_cards(self):
        """Clear all player cards"""
        # Remove all cards from layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear dictionary
        self.player_cards.clear()
    
    def display_players(self, players, game_save):
        """
        Display player cards for all players
        
        Args:
            players (dict): Dictionary of PlayerData objects
            game_save: GameSave object
        """
        # Clear existing cards
        self.clear_cards()
        
        # Set save loaded state to True when we display players
        self.set_save_loaded_state(True)
        
        # Add each player card in a single column
        for player_id, player_data in players.items():
            # Verify player name is valid
            name = player_data.name
            if not name or name.strip() == "":
                name = f"Player_{player_id[-4:]}"
                print(f"PlayerPage: Empty player name detected, using fallback: {name}")
                # Update in the player data for consistency
                player_data.name = name
            
            # Create card
            card = UserCard(
                player_id=player_id,
                name=name,
                health=player_data.health,
                max_health=player_data.max_health
            )
            
            # Set upgrades
            card.set_upgrades(player_data.upgrades)
            
            # Connect signals
            card.upgrade_changed.connect(self.on_upgrade_changed)
            
            # Add card directly to layout - no container needed
            self.cards_layout.addWidget(card)
            
            # Store reference
            self.player_cards[player_id] = card
        
        # Add spacer at the end
        if len(players) > 0:
            self.cards_layout.addStretch()

    def on_upgrade_changed(self, player_id, upgrade_type, value):
        """
        Handle when an upgrade value changes
        
        Args:
            player_id (str): Player ID
            upgrade_type (str): Type of upgrade
            value (int): New value
        """
        # Forward the signal
        self.data_changed.emit()
        
        # If this is the health upgrade, update max health display
        if upgrade_type == "health":
            # Calculate new max health
            max_health = 100 + (value * 20)
            
            # Update card display
            if player_id in self.player_cards:
                card = self.player_cards[player_id]
                card.update_data(card.health, max_health)
    
    def update_player_avatars(self, player_id, avatar_path):
        """
        Update a player's avatar
        
        Args:
            player_id (str): Player ID
            avatar_path (str): Path to avatar image
        """
        import os
        print(f"PlayerPage: Updating avatar for {player_id}: {avatar_path}")
        
        if not avatar_path or not os.path.exists(avatar_path):
            print(f"PlayerPage: Avatar path is invalid: {avatar_path}")
            return
        
        if player_id in self.player_cards:
            print(f"PlayerPage: Found player card for {player_id}, updating avatar")
            self.player_cards[player_id].set_avatar(avatar_path)
        else:
            print(f"PlayerPage: No player card found for {player_id}")
    
    def update_player_health(self, player_id, health, max_health):
        """
        Update a player's health display
        
        Args:
            player_id (str): Player ID
            health (int): Current health
            max_health (int): Maximum health
        """
        if player_id in self.player_cards:
            self.player_cards[player_id].update_data(health, max_health)
    
    def on_add_player_clicked(self):
        """Handle add player button clicked"""
        # First check if a save file is loaded
        if not self.is_save_loaded():
            QMessageBox.warning(
                self,
                "No Save Loaded",
                "Please load a save file first before adding players."
            )
            return
        
        try:
            # Import the user selection dialog
            from ..dialogs.user_selection_dialog import UserSelectionDialog
            from ...core.user_cache import UserCache
            
            # Create user cache if not already there
            if not hasattr(self, 'user_cache') or self.user_cache is None:
                self.user_cache = UserCache()
            
            # Create and show dialog
            dialog = UserSelectionDialog(self.user_cache, self.steam_api, self)
            
            # Connect the users_selected signal
            dialog.users_selected.connect(self.on_users_selected)
            
            # Show dialog
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while opening the user selection dialog: {str(e)}"
            )
            import traceback
            traceback.print_exc()
    
    def on_users_selected(self, selected_users):
        """
        Handle when users are selected from the dialog
        
        Args:
            selected_users (list): List of (steam_id, username) tuples
        """
        print(f"DEBUG Dialog: Emitting users_selected with data: {selected_users}")
        
        if not selected_users:
            print("No users selected")
            return
        
        # Process each selected user
        for index, (steam_id, username) in enumerate(selected_users):
            print(f"PlayerPage: Emitting add_player_requested for {steam_id}, name: {username}")
            
            # Make sure username is not empty
            if not username or username.strip() == "":
                username = f"Player_{steam_id[-4:]}"
                print(f"Empty username detected, using fallback: {username}")
                
            # Emit signal to add to game save - explicitly pass both parameters
            self.add_player_requested.emit(steam_id, username)
            
            # Small delay between adding multiple players to ensure UI updates properly
            if index < len(selected_users) - 1:  # If not the last user
                from PySide6.QtCore import QCoreApplication
                QCoreApplication.processEvents()  # Process pending events
    
    def reset_changes(self):
        """Reset all changes to original values"""
        # This will be handled by connecting to main window
        # which will reload the original data
        pass
    
    def set_steam_api(self, steam_api):
        """Set the reference to the steam API"""
        self.steam_api = steam_api
        
    def set_save_loaded_state(self, is_loaded):
        """
        Set whether a save file is currently loaded
        
        Args:
            is_loaded (bool): Whether a save is loaded
        """
        print(f"PlayerPage: Setting save loaded state to {is_loaded}")
        self._save_loaded = is_loaded
        
    def is_save_loaded(self):
        """
        Check if a save file is loaded
        
        Returns:
            bool: True if a save is loaded, False otherwise
        """
        print(f"PlayerPage: Checking save loaded state: {self._save_loaded}")
        return self._save_loaded