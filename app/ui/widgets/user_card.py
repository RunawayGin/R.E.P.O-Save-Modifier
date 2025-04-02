from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QSizePolicy, QPushButton, QApplication, QSlider
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
import os

# Import the ValueEditor from your widgets module.
# Adjust the import path as needed.
from ..widgets.value_editor import ValueEditor

class UserCard(QFrame):
    """
    Card widget displaying user information with an expandable upgrade section.
    Now uses ValueEditor for upgrade controls to match the styling in Player Upgrades.
    """
    
    # Signals
    edit_clicked = Signal(str)  # player_id
    upgrade_changed = Signal(str, str, int)  # player_id, upgrade_type, value
    
    def __init__(self, player_id, name="Unknown", health=100, max_health=100, 
                avatar_path=None, parent=None):
        super().__init__(parent)
        
        # Store player data
        self.player_id = player_id
        
        # Handle empty name and fallback
        if not name or name.strip() == "":
            name = f"Player_{player_id[-4:]}"
            print(f"UserCard: Empty name received, using fallback: {name}")
        
        self.player_name = name
        self.health = health
        self.max_health = max_health
        self.avatar_path = avatar_path
        
        # Initialize upgrades with default values
        self.upgrades = {
            "health": 0,
            "stamina": 0,
            "extraJump": 0,
            "launch": 0,
            "mapPlayerCount": 0,
            "speed": 0,
            "strength": 0,
            "range": 0,
            "throw": 0
        }
        
        # Expansion state for the card
        self.is_expanded = False
        
        # Get app base directory for resources
        self.app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        self.icons_dir = os.path.join(self.app_dir, 'resources', 'icons')
        
        # Set up the UI components
        self.setup_ui()
        self.update_data(self.health, self.max_health)
        
        # Debug log
        print(f"UserCard initialized for player {player_id} with name '{self.player_name}' and upgrades: {self.upgrades}")
    
    def setup_ui(self):
        """Set up the UI components."""
        self.setObjectName("user_card")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet("""
            #user_card {
                background-color: #343b48 !important;
                border-radius: 10px !important;
                border: 1px solid #343b48 !important;
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Top section: avatar, name, and health info
        top_section = QFrame()
        top_section.setObjectName("top_section")
        top_section.setStyleSheet("""
            #top_section {
                background-color: #343b48 !important;
                border: none;
            }
        """)
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(64, 64)
        self.avatar_label.setScaledContents(True)
        self.avatar_label.setObjectName("user_avatar")
        self.avatar_label.setStyleSheet("""
            #user_avatar {
                background-color: #343b48 !important;
                border-radius: 32px;
                border: none;
            }
        """)
        if self.avatar_path:
            self.set_avatar(self.avatar_path)
        header_layout.addWidget(self.avatar_label)
        
        name_layout = QVBoxLayout()
        self.name_label = QLabel(self.player_name)
        self.name_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #dce1ec;")
        self.id_label = QLabel(f"ID: {self.player_id}")
        self.id_label.setStyleSheet("font-size: 9pt; color: #8a95aa;")
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.id_label)
        name_layout.addStretch()
        header_layout.addLayout(name_layout)
        header_layout.addStretch()
        top_layout.addLayout(header_layout)
        
        # Health section with slider
        health_layout = QVBoxLayout()
        health_layout.setSpacing(5)
        health_header_layout = QHBoxLayout()
        health_label = QLabel("Health")
        health_label.setStyleSheet("font-size: 12pt; color: #dce1ec;")
        self.health_value_label = QLabel(f"{self.health}/{self.max_health}")
        self.health_value_label.setStyleSheet("font-size: 12pt; color: #568af2; font-weight: bold;")
        health_header_layout.addWidget(health_label)
        health_header_layout.addStretch()
        health_header_layout.addWidget(self.health_value_label)
        health_layout.addLayout(health_header_layout)
        
        # Health slider
        self.health_slider = QSlider(Qt.Horizontal)
        self.health_slider.setObjectName("player_health_slider")
        self.health_slider.setMinimum(1)  # Can't go below 1 health
        self.health_slider.setMaximum(self.max_health)
        self.health_slider.setValue(self.health)
        self.health_slider.setFixedHeight(20)
        
        # Connect slider to health update
        self.health_slider.valueChanged.connect(self.on_health_slider_changed)
        
        # Style the slider
        self.apply_health_slider_style()
        
        health_layout.addWidget(self.health_slider)
        top_layout.addLayout(health_layout)
        
        self.main_layout.addWidget(top_section)
        
        # Expandable container for upgrade controls
        self.expandable_container = QFrame()
        self.expandable_container.setObjectName("expandable_content")
        self.expandable_container.setStyleSheet("""
            #expandable_content {
                background-color: #343b48;
                border-radius: 5px;
            }
        """)
        self.expandable_layout = QVBoxLayout(self.expandable_container)
        self.expandable_layout.setContentsMargins(0, 10, 0, 10)
        self.expandable_layout.setSpacing(4)
        self.main_layout.addWidget(self.expandable_container)
        self.expandable_container.hide()
        
        # Action row with edit button
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        self.edit_button = QPushButton("Edit")
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #568af2; #343b48 is the gray
                color: #568af2;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #568af2;
                color: white;
            }
        """)
        self.edit_button.clicked.connect(self.toggle_expand)
        actions_layout.addWidget(self.edit_button)
        self.main_layout.addLayout(actions_layout)
    
    def toggle_expand(self):
        """Toggle the expanded state of the card."""
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.edit_button.setText("Close")
            # Only build the layout if it hasn't been built yet
            if not self.expandable_layout.count():
                self.create_upgrade_controls()
            self.expandable_container.show()
        else:
            self.edit_button.setText("Edit")
            self.expandable_container.hide()
        self.adjustSize()
        if self.parent():
            self.parent().adjustSize()
    
    def create_upgrade_controls(self):
        """Create upgrade controls for the expandable section."""
        # Movement Upgrades Section
        self.add_section_header("Movement Upgrades")
        movement_layout = QHBoxLayout()
        movement_layout.setSpacing(8)
        
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        left_col.addWidget(self.create_upgrade_row("Speed", "speed", self.upgrades.get("speed", 0)))
        left_col.addWidget(self.create_upgrade_row("Extra Jump", "extraJump", self.upgrades.get("extraJump", 0)))
        
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        right_col.addWidget(self.create_upgrade_row("Stamina", "stamina", self.upgrades.get("stamina", 0)))
        right_col.addWidget(self.create_upgrade_row("Launch", "launch", self.upgrades.get("launch", 0)))
        
        movement_layout.addLayout(left_col)
        movement_layout.addLayout(right_col)
        self.expandable_layout.addLayout(movement_layout)
        
        # Combat Upgrades Section
        self.add_section_header("Combat Upgrades")
        combat_layout = QHBoxLayout()
        combat_layout.setSpacing(8)
        
        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        left_col.addWidget(self.create_upgrade_row("Health", "health", self.upgrades.get("health", 0)))
        left_col.addWidget(self.create_upgrade_row("Range", "range", self.upgrades.get("range", 0)))
        
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        right_col.addWidget(self.create_upgrade_row("Strength", "strength", self.upgrades.get("strength", 0)))
        right_col.addWidget(self.create_upgrade_row("Throw", "throw", self.upgrades.get("throw", 0)))
        
        combat_layout.addLayout(left_col)
        combat_layout.addLayout(right_col)
        self.expandable_layout.addLayout(combat_layout)
        
        # Special Upgrades Section
        self.add_section_header("Special Upgrades")
        self.expandable_layout.addWidget(
            self.create_upgrade_row("Map Player Count", "mapPlayerCount", self.upgrades.get("mapPlayerCount", 0))
        )
    
    def add_section_header(self, title):
        """Add a section header to the expandable content."""
        header_container = QFrame()
        header_container.setObjectName("section_header")
        header_container.setStyleSheet("""
            #section_header {
                background-color: #343b48; 
                min-height: 30px;
                margin-top: 5px;
                margin-bottom: 0px;
            }
        """)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header = QLabel(title)
        header.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: #dce1ec;
        """)
        header_layout.addWidget(header)
        self.expandable_layout.addWidget(header_container)
    
    def create_upgrade_row(self, label, upgrade_type, value):
        """
        Create a row for an upgrade using the ValueEditor directly without additional framing.
        """
        # Create and add the ValueEditor with the label included
        editor = ValueEditor(
            key=upgrade_type,
            label=label,  # Pass the label text directly to ValueEditor
            value=value,
            value_type="int",
            min_value=0,
            max_value=9999
        )
        # Connect the value change signal
        editor.value_changed.connect(lambda k, v, utype=upgrade_type: self.on_upgrade_value_changed(utype, v))
        
        # Style the editor to match the design expectations
        editor.setObjectName(f"upgrade_editor_{upgrade_type}")
        editor.setStyleSheet(f"""
            #{editor.objectName()} {{
                background-color: #20242c;
                border-radius: 5px;
                min-height: 36px;
                max-height: 36px;
            }}
        """)
        
        return editor
    
    def on_upgrade_value_changed(self, upgrade_type, new_value):
        """
        Handle value changes from the ValueEditor widget and emit the upgrade_changed signal.
        
        Args:
            upgrade_type (str): Type of upgrade
            new_value (int): New value
        """
        # CRITICAL: Store the new value in the upgrades dictionary
        self.upgrades[upgrade_type] = new_value
        
        # Log for debugging
        print(f"UserCard {self.player_id}: Upgrade {upgrade_type} set to {new_value}")
        print(f"UserCard {self.player_id}: Updated upgrades dict: {self.upgrades}")
        
        # Emit the signal for parent widgets
        self.upgrade_changed.emit(self.player_id, upgrade_type, new_value)
    
    # Custom method to get all current upgrade values
    def get_all_upgrades(self):
        """
        Get all current upgrade values from the card.
        
        Returns:
            dict: Dictionary of upgrade types and their current values
        """
        return self.upgrades.copy()  # Return a copy to prevent external modifications
    
    def on_health_slider_changed(self, value):
        """Handle changes to the health slider."""
        # Update the health display
        self.health = value
        self.health_value_label.setText(f"{self.health}/{self.max_health}")
        
        # Update the slider style based on new health percentage
        self.apply_health_slider_style()
        
        # Emit signal to update the player's health in the game data
        self.upgrade_changed.emit(self.player_id, "playerHealth", value)
    
    def update_data(self, health, max_health):
        """Update the health display on the UI."""
        self.health = health
        self.max_health = max_health
        
        # Update label
        self.health_value_label.setText(f"{self.health}/{self.max_health}")
        
        # Update slider
        self.health_slider.blockSignals(True)  # Prevent feedback loop
        self.health_slider.setMaximum(max_health)
        self.health_slider.setValue(health)
        self.health_slider.blockSignals(False)
        
        # Update styling
        self.apply_health_slider_style()
    
    def apply_health_slider_style(self):
        """Apply styling to the health slider with a color that smoothly transitions based on health percentage."""
        health_percent = (self.health / self.max_health) * 100 if self.max_health > 0 else 0
        
        # Calculate a smooth color transition
        if health_percent <= 50:
            # Red (0%) to Yellow (50%)
            ratio = health_percent / 50.0
            r = 231  # Red component stays high
            g = int(39 + (156 * ratio))  # Green increases
            b = 60   # Blue stays low
        else:
            # Yellow (50%) to Green (100%)
            ratio = (health_percent - 50) / 50.0
            r = int(231 - (185 * ratio))  # Red decreases
            g = 195  # Green stays high
            b = 60   # Blue stays low
        
        # Format as hex color
        color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Apply styling to slider with calculated color
        self.health_slider.setStyleSheet(f"""
            QSlider#player_health_slider {{
                background: transparent;
                padding: 0px;
            }}
            
            QSlider#player_health_slider::groove:horizontal {{
                border: 1px solid #3a4052;
                height: 10px;
                background: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, 
                                        stop:0 #282f3d, stop:1 #30384a);
                margin: 0px;
                border-radius: 5px;
            }}
            
            QSlider#player_health_slider::sub-page:horizontal {{
                background: {color};
                border: 1px solid #3a4052;
                height: 10px;
                border-radius: 5px;
            }}
            
            QSlider#player_health_slider::handle:horizontal {{
                background: white;
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 9px;
                border: 1px solid #3a4052;
            }}
            
            QSlider#player_health_slider::handle:horizontal:hover {{
                background: #dce1ec;
            }}
        """)
    
    def interpolate_color(self, color1, color2, weight):
        """
        Interpolate between two colors based on weight.
        Weight 0.0 returns color2, weight 1.0 returns color1.
        """
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        c1 = hex_to_rgb(color1)
        c2 = hex_to_rgb(color2)
        
        r = int(c1[0] * weight + c2[0] * (1 - weight))
        g = int(c1[1] * weight + c2[1] * (1 - weight))
        b = int(c1[2] * weight + c2[2] * (1 - weight))
        
        return rgb_to_hex((r, g, b))
    
    def set_avatar(self, avatar_path):
        """
        Set the avatar image.
        """
        pixmap = QPixmap(avatar_path)
        if not pixmap.isNull():
            self.avatar_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def set_upgrades(self, upgrades_dict):
        """
        Set the player's upgrades from outside and store them in self.upgrades.
        This method is called by external code (e.g. PlayerPage) so that
        the card knows which upgrades to display.
        """
        if not isinstance(upgrades_dict, dict):
            return
        self.upgrades.update(upgrades_dict)
        # If the card is already expanded, rebuild or refresh the layout so new values show.
        if self.is_expanded:
            # Clear existing controls
            while self.expandable_layout.count():
                item = self.expandable_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # Re-create upgrade controls with updated data
            self.create_upgrade_controls()
        self.update()  # Force a repaint if necessary