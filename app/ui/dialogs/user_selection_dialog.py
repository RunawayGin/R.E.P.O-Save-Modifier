# Add this to a new file: app/ui/dialogs/user_selection_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QWidget, QCheckBox, QFrame, QRadioButton, QButtonGroup,
    QTabWidget, QGroupBox, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont

from ...core.user_cache import UserCache, CachedUser

import os

class UserSelectionDialog(QDialog):
    """
    Dialog for selecting users from cache or adding new users
    """
    
    # Signal when users are selected
    users_selected = Signal(list)  # List of (steam_id, username) tuples
    
    def __init__(self, user_cache, steam_api, parent=None):
        """
        Initialize the dialog
        
        Args:
            user_cache (UserCache): User cache instance
            steam_api: Steam API instance for fetching avatars
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        self.user_cache = user_cache
        self.steam_api = steam_api
        self.selected_users = []  # List to store selected users
        
        # Set window properties
        self.setWindowTitle("Add Players")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Create layout
        self.setup_ui()
        
        # Load cached users
        self.load_cached_users()
        
        # Explicitly ensure Add button is disabled at start
        print("Initially disabling Add Selected button")
        if hasattr(self, 'add_button'):
            self.add_button.setEnabled(False)
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_cached_users_tab()
        self.create_new_user_tab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.cached_users_tab, "Select Cached Users")
        self.tab_widget.addTab(self.new_user_tab, "Add New User")
        
        main_layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.add_button = QPushButton("Add Selected")
        self.add_button.setEnabled(False)  # CRITICAL: Start with button disabled!
        self.add_button.clicked.connect(self.accept_selection)
        self.add_button.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #627291;
                color: #a0a8b7;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_button)
        
        main_layout.addLayout(button_layout)
        
        print("Setup UI completed, add_button created and disabled")
    
    def create_cached_users_tab(self):
        """Create the tab for selecting cached users"""
        self.cached_users_tab = QWidget()
        
        # Layout
        layout = QVBoxLayout(self.cached_users_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title and description
        title = QLabel("Select Cached Users")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        description = QLabel("Select one or more users from the list below to add to your game save.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create scroll area for user items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.users_container = QWidget()
        self.users_layout = QVBoxLayout(self.users_container)
        self.users_layout.setContentsMargins(0, 0, 0, 0)
        self.users_layout.setSpacing(5)
        
        # Empty state message
        self.empty_message = QLabel("No cached users found. Add a new user first.")
        self.empty_message.setAlignment(Qt.AlignCenter)
        self.empty_message.setStyleSheet("color: #8a95aa; padding: 20px;")
        self.users_layout.addWidget(self.empty_message)
        
        # Add stretch at the end
        self.users_layout.addStretch()
        
        scroll.setWidget(self.users_container)
        layout.addWidget(scroll)
        
        # Buttons for managing cached users
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_users)
        
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all_users)
        
        buttons_layout.addWidget(self.select_all_button)
        buttons_layout.addWidget(self.deselect_all_button)
        
        layout.addLayout(buttons_layout)
    
    def create_new_user_tab(self):
        """Create the tab for adding a new user"""
        self.new_user_tab = QWidget()
        
        # Layout
        layout = QVBoxLayout(self.new_user_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title and description
        title = QLabel("Add New User")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        description = QLabel("Enter a Steam ID to fetch player information. This user will be added to your game save and cached for future use.")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Steam ID input
        id_layout = QHBoxLayout()
        id_label = QLabel("Steam ID:")
        id_label.setMinimumWidth(80)
        
        self.steam_id_input = QLineEdit()
        self.steam_id_input.setPlaceholderText("17-digit number (e.g. 76561198012345678)")
        
        self.fetch_button = QPushButton("Fetch")
        self.fetch_button.setMinimumWidth(100)
        self.fetch_button.clicked.connect(self.fetch_steam_user)
        
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.steam_id_input)
        id_layout.addWidget(self.fetch_button)
        
        layout.addLayout(id_layout)
        
        # User info display
        self.user_info_box = QGroupBox("User Preview")
        self.user_info_box.setVisible(False)  # Hidden until fetched
        
        info_layout = QHBoxLayout(self.user_info_box)
        
        # Avatar
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(64, 64)
        self.avatar_label.setStyleSheet("border-radius: 32px; background-color: #343b48;")
        info_layout.addWidget(self.avatar_label)
        
        # User details
        details_layout = QVBoxLayout()
        
        self.username_label = QLabel()
        self.username_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        
        self.steam_id_label = QLabel()
        self.steam_id_label.setStyleSheet("color: #8a95aa;")
        
        details_layout.addWidget(self.username_label)
        details_layout.addWidget(self.steam_id_label)
        details_layout.addStretch()
        
        info_layout.addLayout(details_layout)
        info_layout.addStretch()
        
        layout.addWidget(self.user_info_box)
        
        # Add user button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.add_new_user_button = QPushButton("Add This User")
        self.add_new_user_button.setVisible(False)  # Hidden until fetched
        self.add_new_user_button.clicked.connect(self.add_fetched_user)
        self.add_new_user_button.setStyleSheet("""
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
        
        button_layout.addWidget(self.add_new_user_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def load_cached_users(self):
        """Load and display cached users"""
        # Clear current items
        self.clear_user_items()
        
        # Get users from cache
        users = self.user_cache.get_all_users(sort_by_recent=True)
        
        # Show empty message if no users
        if not users:
            self.empty_message.setVisible(True)
            self.select_all_button.setEnabled(False)
            self.deselect_all_button.setEnabled(False)
            return
        
        # Hide empty message
        self.empty_message.setVisible(False)
        self.select_all_button.setEnabled(True)
        self.deselect_all_button.setEnabled(True)
        
        # Create item for each user
        for user in users:
            self.add_user_item(user)
    
    def add_user_item(self, user):
        """
        Add a user item to the list
        
        Args:
            user (CachedUser): Cached user data
        """
        # Create container frame
        item = QFrame()
        item.setObjectName(f"user_item_{user.steam_id}")
        item.setFrameShape(QFrame.StyledPanel)
        item.setStyleSheet("""
            QFrame {
                background-color: #343b48;
                border-radius: 5px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #3a4155;
            }
        """)
        
        # Debug print to verify user data
        print(f"Adding user item: {user.steam_id}, username: '{user.username}'")
        
        # Layout
        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox.setObjectName(f"checkbox_{user.steam_id}")
        checkbox.setStyleSheet("""
            QCheckBox {
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
        # Make sure parameters are captured properly in the lambda
        username_copy = user.username
        steam_id_copy = user.steam_id
        
        # Connect stateChanged signal with explicit parameters to avoid closure issues
        checkbox.stateChanged.connect(
            lambda state, sid=steam_id_copy, name=username_copy: 
            self.on_user_selected(sid, name, state)
        )
        
        layout.addWidget(checkbox)
        
        # Avatar
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setScaledContents(True)
        
        if user.avatar_path and os.path.exists(user.avatar_path):
            pixmap = QPixmap(user.avatar_path)
            avatar.setPixmap(pixmap)
        else:
            # Default avatar background
            avatar.setStyleSheet("background-color: #495166; border-radius: 16px;")
        
        layout.addWidget(avatar)
        
        # Username
        username_label = QLabel(user.username)
        username_label.setObjectName(f"username_{user.steam_id}")
        username_label.setStyleSheet("font-weight: bold; color: #dce1ec;")
        
        # Debug verification
        print(f"Created username label with text: '{username_label.text()}'")
        
        layout.addWidget(username_label)
        
        # Steam ID (less prominent)
        steam_id_label = QLabel(user.steam_id)
        steam_id_label.setObjectName(f"steam_id_{user.steam_id}")
        steam_id_label.setStyleSheet("color: #8a95aa; font-size: 9pt;")
        steam_id_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(steam_id_label)
        
        # Add to users layout
        self.users_layout.insertWidget(self.users_layout.count() - 1, item)
    
    def clear_user_items(self):
        """Clear all user items from the list"""
        # Remove all items except the empty message and stretch
        while self.users_layout.count() > 2:
            item = self.users_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset selected users
        self.selected_users = []
        self.update_add_button()
    
    def on_user_selected(self, steam_id, username, state):
        """
        Handle when a user is selected
        
        Args:
            steam_id (str): Steam ID
            username (str): Username
            state (int): Checkbox state
        """
        print(f"Selection changed for {steam_id} ({username}): state = {state}")
        
        # In Qt, CheckState.Checked is 2, not 1
        if state == 2:  # Qt.Checked (explicitly compare with 2)
            # Add to selected users if not already there
            if steam_id not in [u[0] for u in self.selected_users]:
                self.selected_users.append((steam_id, username))
                print(f"Added user to selection: {steam_id}, {username}")
        else:
            # Remove from selected users
            self.selected_users = [u for u in self.selected_users if u[0] != steam_id]
            print(f"Removed user from selection: {steam_id}")
        
        # Directly set button state based on selection count
        has_selection = len(self.selected_users) > 0
        print(f"Setting add button enabled: {has_selection} (selection count: {len(self.selected_users)})")
        self.add_button.setEnabled(has_selection)
        
        # Debug print the button state to verify
        print(f"Verified button enabled state: {self.add_button.isEnabled()}")

    def update_add_button(self):
        """Update the state of the add button based on selection"""
        has_selection = len(self.selected_users) > 0
        self.add_button.setEnabled(has_selection)
        
        # Debug print
        print(f"Updating add button state: {has_selection}")

    def select_all_users(self):
        """Select all users in the list"""
        # Clear current selections to avoid duplicates
        self.selected_users = []
        
        # Go through all user frames
        for i in range(self.users_layout.count() - 1):  # Skip stretch
            item = self.users_layout.itemAt(i).widget()
            if isinstance(item, QFrame) and item.objectName().startswith("user_item_"):
                # Extract the steam_id from the objectName
                steam_id = item.objectName().replace("user_item_", "")
                
                # Find the username by looking through children
                username = None
                for child in item.children():
                    if isinstance(child, QLabel) and child.objectName() == f"username_{steam_id}":
                        username = child.text()
                        print(f"Found username label with text: '{username}'")
                        break
                
                # If couldn't find username, try getting from cache
                if not username and hasattr(self, 'user_cache'):
                    user = self.user_cache.get_user(steam_id)
                    if user:
                        username = user.username
                        print(f"Got username from cache: '{username}'")
                
                # Final fallback
                if not username:
                    username = f"Player_{steam_id[-4:]}"
                    print(f"Using fallback username: '{username}'")
                
                # Add to selected_users
                self.selected_users.append((steam_id, username))
                print(f"Added to selected_users: {steam_id}, '{username}'")
                
                # Check the checkbox
                for child in item.children():
                    if isinstance(child, QCheckBox):
                        child.blockSignals(True)
                        child.setChecked(True)
                        child.blockSignals(False)
                        break
        
        # Update add button state
        self.update_add_button()
        
        # Debug print
        print(f"Selected users after select_all: {self.selected_users}")
    
    def deselect_all_users(self):
        """Deselect all users in the list"""
        for i in range(self.users_layout.count() - 1):  # Skip stretch
            item = self.users_layout.itemAt(i).widget()
            if isinstance(item, QFrame) and item.objectName().startswith("user_item_"):
                # Find the checkbox
                for child in item.children():
                    if isinstance(child, QCheckBox):
                        child.setChecked(False)
                        break
    
    def fetch_steam_user(self):
        """Fetch user data from Steam"""
        # Get Steam ID
        steam_id = self.steam_id_input.text().strip()
        
        # Validate
        if not steam_id or not steam_id.isdigit() or len(steam_id) != 17:
            QMessageBox.warning(
                self,
                "Invalid Steam ID",
                "Please enter a valid 17-digit Steam ID."
            )
            return
        
        # Check if already in cache
        cached_user = self.user_cache.get_user(steam_id)
        if cached_user:
            # Just show the cached user
            self.display_fetched_user(steam_id, cached_user.username, cached_user.avatar_path)
            return
        
        # Show loading state
        self.fetch_button.setEnabled(False)
        self.fetch_button.setText("Fetching...")
        
        # Use a QTimer to avoid freezing the UI
        from PySide6.QtCore import QTimer
        
        def do_fetch():
            try:
                # Fetch user info
                info = self.steam_api.fetch_profile_info(steam_id)
                
                # Reset button state
                self.fetch_button.setEnabled(True)
                self.fetch_button.setText("Fetch")
                
                if not info or 'steamID' not in info:
                    QMessageBox.warning(
                        self,
                        "User Not Found",
                        "Could not find a Steam user with that ID. Please check the ID and try again."
                    )
                    return
                
                # Get username
                username = info.get('steamID', f"User_{steam_id[-4:]}")
                
                # Try to fetch avatar
                avatar_path = None
                try:
                    avatar_path = self.steam_api.fetch_avatar(steam_id)
                except:
                    pass  # Skip if avatar fetch fails
                
                # Display user
                self.display_fetched_user(steam_id, username, avatar_path)
                
            except Exception as e:
                # Reset button state
                self.fetch_button.setEnabled(True)
                self.fetch_button.setText("Fetch")
                
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while fetching user data: {str(e)}"
                )
        
        # Execute after a short delay to allow the UI to update
        QTimer.singleShot(100, do_fetch)
    
    def display_fetched_user(self, steam_id, username, avatar_path=None):
        """
        Display fetched user data
        
        Args:
            steam_id (str): Steam ID
            username (str): Username
            avatar_path (str, optional): Path to avatar image. Defaults to None.
        """
        # Store data for adding
        self.fetched_user = {
            'steam_id': steam_id,
            'username': username,
            'avatar_path': avatar_path
        }
        
        # Update the UI
        self.username_label.setText(username)
        self.steam_id_label.setText(f"Steam ID: {steam_id}")
        
        # Set avatar if available
        if avatar_path and os.path.exists(avatar_path):
            pixmap = QPixmap(avatar_path)
            self.avatar_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Clear avatar
            self.avatar_label.clear()
            self.avatar_label.setStyleSheet("background-color: #343b48; border-radius: 32px;")
        
        # Show the user info box and add button
        self.user_info_box.setVisible(True)
        self.add_new_user_button.setVisible(True)
    
    def add_fetched_user(self):
        """Add the fetched user to the selection and cache"""
        if hasattr(self, 'fetched_user'):
            # Add to cache
            self.user_cache.add_user(
                self.fetched_user['steam_id'],
                self.fetched_user['username'],
                self.fetched_user['avatar_path']
            )
            
            # Add to selected users
            self.selected_users = [(
                self.fetched_user['steam_id'],
                self.fetched_user['username']
            )]
            
            # Enable the add button
            self.update_add_button()
            
            # Accept the dialog
            self.accept()
    
    def accept_selection(self):
        """Accept the dialog with selected users"""
        if self.selected_users:
            print(f"DEBUG Dialog: Emitting users_selected with data: {self.selected_users}")
            
            # Verify each user has a valid username
            valid_users = []
            for steam_id, username in self.selected_users:
                if not username or username.strip() == "":
                    username = f"Player_{steam_id[-4:]}"
                    print(f"Fixed empty username for {steam_id}, now: {username}")
                valid_users.append((steam_id, username))
            
            self.selected_users = valid_users
            
            # Update last used timestamp for each selected user
            for steam_id, _ in self.selected_users:
                self.user_cache.update_last_used(steam_id)
            
            # Emit signal with selected users
            self.users_selected.emit(self.selected_users)
            
            # Close dialog
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one user to add."
            )
