from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QSizePolicy, QLineEdit, QSpinBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..widgets import ModernButton, ValueEditor

class GameStatsPage(QWidget):
    """
    Page for editing game statistics and run information
    """
    
    # Signals
    data_changed = Signal()  # Emitted when any data changes
    
    def __init__(self, parent=None):
        """
        Initialize the game stats page
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Set up UI
        self.setup_ui()
        
        # Game save reference
        self.game_save = None
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Page title
        title = QLabel("Game Stats")
        title.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #dce1ec;
        """)
        main_layout.addWidget(title)
        
        # Description
        description = QLabel(
            "Edit game statistics like levels, currency, and lives."
        )
        description.setStyleSheet("""
            font-size: 11pt;
            color: #8a95aa;
        """)
        main_layout.addWidget(description)
        
        # Team name section
        team_frame = QFrame()
        team_frame.setStyleSheet(f"""
            background-color: #272c36;
            border-radius: 8px;
            border: 1px solid #343b48;
        """)

        team_layout = QHBoxLayout(team_frame)
        team_layout.setContentsMargins(15, 15, 15, 15)

        team_label = QLabel("Team Name:")
        team_label.setStyleSheet("""
            font-size: 12pt;
            color: #dce1ec;
        """)

        self.team_name_input = QLineEdit()
        self.team_name_input.setStyleSheet("""
            background-color: #2c313c;
            color: #dce1ec;
            border: 1px solid #343b48;
            border-radius: 5px;
            padding: 5px;
            font-size: 12pt;
        """)
        self.team_name_input.textChanged.connect(self.on_team_name_changed)

        team_layout.addWidget(team_label)
        team_layout.addWidget(self.team_name_input)

        main_layout.addWidget(team_frame)
        
        # Stats section
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")
        stats_frame.setStyleSheet("""
            #stats_frame {
                background-color: #272c36;
                border-radius: 8px;
                border: 1px solid #343b48;
            }
        """)
        
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        stats_layout.setSpacing(15)
        
        # Create editors for all stats
        self.level_editor = self.create_stat_editor("Level", "level", 1, 1, 1000)
        self.currency_editor = self.create_stat_editor("Currency", "currency", 0, 0, 3)
        self.lives_editor = self.create_stat_editor("Lives", "lives", 1, 1, 6)
        self.charge_editor = self.create_stat_editor("Charging Station", "charging", 0, 0, 12)
        self.haul_editor = self.create_stat_editor("Total Haul", "haul", 0, 0, 999999)
        self.save_level_editor = self.create_stat_editor("Save Level", "savelevel", 0, 0, 100)
        
        # Add editors to layout
        stats_layout.addWidget(self.level_editor)
        stats_layout.addWidget(self.currency_editor)
        stats_layout.addWidget(self.lives_editor)
        stats_layout.addWidget(self.charge_editor)
        stats_layout.addWidget(self.haul_editor)
        stats_layout.addWidget(self.save_level_editor)
        
        main_layout.addWidget(stats_frame)
        
        # Bottom buttons - save and reset
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.reset_button = ModernButton("Reset Changes", "medium")
        self.reset_button.clicked.connect(self.reset_changes)
        
        buttons_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Add stretch to push content to the top
        main_layout.addStretch()
    
    def create_stat_editor(self, label, key, default_value=0, min_value=0, max_value=9999):
        """
        Create a ValueEditor for a game stat
        
        Args:
            label (str): Display label
            key (str): Internal key
            default_value (int, optional): Default value. Defaults to 0.
            min_value (int, optional): Minimum value. Defaults to 0.
            max_value (int, optional): Maximum value. Defaults to 9999.
            
        Returns:
            ValueEditor: The created editor
        """
        editor = ValueEditor(
            key=key,
            label=label,
            value=default_value,
            value_type="int",
            min_value=min_value,
            max_value=max_value
        )
        editor.value_changed.connect(self.on_stat_changed)
        return editor
    
    def display_game_save(self, game_save):
        """
        Display game save data
        
        Args:
            game_save: GameSave object
        """
        if not game_save:
            return
            
        self.game_save = game_save
        
        # Update team name
        self.team_name_input.setText(game_save.team_name)
        
        # Update stats without triggering signals
        self.level_editor.blockSignals(True)
        self.level_editor.set_value(game_save.get_level())
        self.level_editor.blockSignals(False)
        
        self.currency_editor.blockSignals(True)
        self.currency_editor.set_value(game_save.get_currency())
        self.currency_editor.blockSignals(False)
        
        self.lives_editor.blockSignals(True)
        self.lives_editor.set_value(game_save.get_lives())
        self.lives_editor.blockSignals(False)
        
        self.charge_editor.blockSignals(True)
        self.charge_editor.set_value(game_save.get_charging_station_charge())
        self.charge_editor.blockSignals(False)
        
        self.haul_editor.blockSignals(True)
        self.haul_editor.set_value(game_save.get_total_haul())
        self.haul_editor.blockSignals(False)
        
        self.save_level_editor.blockSignals(True)
        self.save_level_editor.set_value(game_save.get_save_level())
        self.save_level_editor.blockSignals(False)
    
    def on_team_name_changed(self, text):
        """
        Handle when team name changes
        
        Args:
            text (str): New team name
        """
        if self.game_save:
            self.game_save.team_name = text
            self.data_changed.emit()
    
    def on_stat_changed(self, key, value):
        """
        Handle when a stat value changes
        
        Args:
            key (str): Stat key
            value: New value
        """
        if not self.game_save:
            return
            
        # Update the appropriate stat
        if key == "level":
            self.game_save.set_level(value)
        elif key == "currency":
            self.game_save.set_currency(value)
        elif key == "lives":
            self.game_save.set_lives(value)
        elif key == "charging":
            self.game_save.set_charging_station_charge(value)
        elif key == "haul":
            self.game_save.set_total_haul(value)
        elif key == "savelevel":
            self.game_save.set_save_level(value)
        
        # Emit signal
        self.data_changed.emit()
    
    def reset_changes(self):
        """Reset all changes to original values"""
        if self.game_save:
            # Redisplay the current game save data
            self.display_game_save(self.game_save)
    
    def get_team_name(self):
        """
        Get the current team name
        
        Returns:
            str: Team name
        """
        return self.team_name_input.text()