from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QGroupBox, QSizePolicy,
    QSpacerItem, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..widgets import ModernButton, ValueEditor

class UpgradesPage(QWidget):
    """
    Page for editing player upgrades
    """
    
    # Signals
    data_changed = Signal(str, str, int)  # player_id, upgrade_type, value
    
    def __init__(self, parent=None):
        """
        Initialize the upgrades page
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Store editors by player
        self.player_editors = {}  # {player_id: {upgrade_type: ValueEditor}}
        
        # Set up UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Page title
        title = QLabel("Player Upgrades")
        title.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #dce1ec;
        """)
        main_layout.addWidget(title)
        
        # Description
        description = QLabel(
            "Edit player upgrade levels. Each upgrade affects different player abilities."
        )
        description.setStyleSheet("""
            font-size: 11pt;
            color: #8a95aa;
        """)
        main_layout.addWidget(description)
        
        # Tab widget for player upgrades
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #343b48;
                border-radius: 5px;
                background-color: #272c36;
            }
            
            QTabBar::tab {
                background-color: #2c313c;
                color: #8a95aa;
                border: 1px solid #343b48;
                border-bottom-color: #272c36;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #272c36;
                color: #dce1ec;
                border-bottom-color: #272c36;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #343b48;
            }
        """)
        
        main_layout.addWidget(self.tab_widget)
        
        # Bottom buttons
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
        # Clear existing tabs
        self.tab_widget.clear()
        
        # Add empty tab
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        
        empty_label = QLabel("No save file loaded. Please load a save file from the Home page.")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            font-size: 14pt;
            color: #8a95aa;
            padding: 40px;
        """)
        
        empty_layout.addWidget(empty_label)
        empty_layout.addStretch()
        
        self.tab_widget.addTab(empty_widget, "No Data")
    
    def display_upgrades(self, players):
        """
        Display upgrades for all players
        
        Args:
            players (dict): Dictionary of PlayerData objects
        """
        # Clear existing tabs and editors
        self.tab_widget.clear()
        self.player_editors.clear()
        
        # No players
        if not players:
            self.display_empty_state()
            return
        
        # Add a tab for each player
        for player_id, player_data in players.items():
            player_widget = self.create_player_tab(player_id, player_data)
            self.tab_widget.addTab(player_widget, player_data.name)
    
    def create_player_tab(self, player_id, player_data):
        """
        Create a tab with upgrade editors for a player
        
        Args:
            player_id (str): Player ID
            player_data: PlayerData object
            
        Returns:
            QWidget: Tab widget
        """
        # Create widget
        player_widget = QWidget()
        
        # Create scroll area for upgrades
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Create container for scrollable content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(15, 15, 15, 15)
        scroll_layout.setSpacing(20)
        
        # Create editors dictionary for this player
        self.player_editors[player_id] = {}
        
        # Create upgrade groups
        scroll_layout.addWidget(self.create_movement_upgrades(player_id, player_data))
        scroll_layout.addWidget(self.create_combat_upgrades(player_id, player_data))
        scroll_layout.addWidget(self.create_special_upgrades(player_id, player_data))
        
        # Add spacer at the end
        scroll_layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(scroll_content)
        
        # Main layout for the tab
        tab_layout = QVBoxLayout(player_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        
        return player_widget
    
    def create_movement_upgrades(self, player_id, player_data):
        """
        Create editors for movement-related upgrades
        
        Args:
            player_id (str): Player ID
            player_data: PlayerData object
            
        Returns:
            QGroupBox: Upgrades group
        """
        group = QGroupBox("Movement Upgrades")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #272c36;
                border: 1px solid #343b48;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
                color: #dce1ec;
                padding-top: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Speed upgrade
        speed_editor = ValueEditor(
            key=f"{player_id}_speed",
            label="Speed",
            value=player_data.upgrades.get("speed", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        speed_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "speed", v))
        layout.addWidget(speed_editor)
        self.player_editors[player_id]["speed"] = speed_editor
        
        # Stamina upgrade
        stamina_editor = ValueEditor(
            key=f"{player_id}_stamina",
            label="Stamina",
            value=player_data.upgrades.get("stamina", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        stamina_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "stamina", v))
        layout.addWidget(stamina_editor)
        self.player_editors[player_id]["stamina"] = stamina_editor
        
        # Extra Jump upgrade
        jump_editor = ValueEditor(
            key=f"{player_id}_extraJump",
            label="Extra Jump",
            value=player_data.upgrades.get("extraJump", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        jump_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "extraJump", v))
        layout.addWidget(jump_editor)
        self.player_editors[player_id]["extraJump"] = jump_editor
        
        # Launch upgrade
        launch_editor = ValueEditor(
            key=f"{player_id}_launch",
            label="Tumble Launch",
            value=player_data.upgrades.get("launch", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        launch_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "launch", v))
        layout.addWidget(launch_editor)
        self.player_editors[player_id]["launch"] = launch_editor
        
        return group
    
    def on_upgrade_changed(self, player_id, upgrade_type, value):
        """
        Handle when an upgrade value changes
        
        Args:
            player_id (str): Player ID
            upgrade_type (str): Type of upgrade
            value (int): New value
        """
        # Emit signal with updated data
        self.data_changed.emit(player_id, upgrade_type, value)
    
    def update_upgrade_value(self, player_id, upgrade_type, value):
        """
        Update an upgrade value in the UI
        
        Args:
            player_id (str): Player ID
            upgrade_type (str): Type of upgrade
            value (int): New value
        """
        if player_id in self.player_editors and upgrade_type in self.player_editors[player_id]:
            # Update without emitting signals
            self.player_editors[player_id][upgrade_type].blockSignals(True)
            self.player_editors[player_id][upgrade_type].set_value(value)
            self.player_editors[player_id][upgrade_type].blockSignals(False)
    
    def reset_changes(self):
        """Reset all changes to original values"""
        # This will be handled by the main window
        pass
    
    def create_combat_upgrades(self, player_id, player_data):
        """
        Create editors for combat-related upgrades
        
        Args:
            player_id (str): Player ID
            player_data: PlayerData object
            
        Returns:
            QGroupBox: Upgrades group
        """
        group = QGroupBox("Combat Upgrades")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #272c36;
                border: 1px solid #343b48;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
                color: #dce1ec;
                padding-top: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Health upgrade
        health_editor = ValueEditor(
            key=f"{player_id}_health",
            label="Health",
            value=player_data.upgrades.get("health", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        health_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "health", v))
        layout.addWidget(health_editor)
        self.player_editors[player_id]["health"] = health_editor
        
        # Strength upgrade
        strength_editor = ValueEditor(
            key=f"{player_id}_strength",
            label="Strength",
            value=player_data.upgrades.get("strength", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        strength_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "strength", v))
        layout.addWidget(strength_editor)
        self.player_editors[player_id]["strength"] = strength_editor
        
        # Range upgrade
        range_editor = ValueEditor(
            key=f"{player_id}_range",
            label="Grab Range",
            value=player_data.upgrades.get("range", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        range_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "range", v))
        layout.addWidget(range_editor)
        self.player_editors[player_id]["range"] = range_editor
        
        # Throw upgrade
        throw_editor = ValueEditor(
            key=f"{player_id}_throw",
            label="Throw Distance",
            value=player_data.upgrades.get("throw", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        throw_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "throw", v))
        layout.addWidget(throw_editor)
        self.player_editors[player_id]["throw"] = throw_editor
        
        return group
    
    def create_special_upgrades(self, player_id, player_data):
        """
        Create editors for special upgrades
        
        Args:
            player_id (str): Player ID
            player_data: PlayerData object
            
        Returns:
            QGroupBox: Upgrades group
        """
        group = QGroupBox("Special Upgrades")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #272c36;
                border: 1px solid #343b48;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
                color: #dce1ec;
                padding-top: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Map Player Count upgrade
        map_player_editor = ValueEditor(
            key=f"{player_id}_mapPlayerCount",
            label="Map Player Count",
            value=player_data.upgrades.get("mapPlayerCount", 0),
            value_type="int",
            min_value=0,
            max_value=10
        )
        map_player_editor.value_changed.connect(lambda k, v: self.on_upgrade_changed(player_id, "mapPlayerCount", v))
        layout.addWidget(map_player_editor)
        self.player_editors[player_id]["mapPlayerCount"] = map_player_editor
        
        return group