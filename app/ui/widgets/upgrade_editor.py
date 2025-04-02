# Create a new file: app/ui/widgets/upgrade_editor.py

from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, 
    QSpinBox, QSizePolicy, QSlider, QPushButton  # Add QPushButton here
)
from PySide6.QtCore import Qt, Signal, QSize, Property

class UpgradeEditor(QFrame):
    """
    Compact upgrade editor widget for player cards
    """
    
    # Signal emitted when value changes
    value_changed = Signal(str, int)  # upgrade_type, value
    
    def __init__(self, upgrade_type, label, value=0, max_value=10, parent=None):
        """
        Initialize the upgrade editor
        
        Args:
            upgrade_type (str): Type of upgrade
            label (str): Display label
            value (int, optional): Initial value. Defaults to 0.
            max_value (int, optional): Maximum value. Defaults to 10.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Store properties
        self._upgrade_type = upgrade_type
        self.label_text = label
        self.max_value = max_value
        
        # Setup UI
        self.setup_ui()
        
        # Set initial value
        self.setValue(value)
    
    def setup_ui(self):
        """Set up the UI components"""
        # Set frame style
        #self.setFrameShape(QFrame.NoFrame)
        self.setMinimumHeight(50)  # Ensure minimum height for each control
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 5, 0, 5)  # Increase vertical padding
        self.main_layout.setSpacing(8)  # Increase spacing between elements
        
        # Header row with label and value
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        # Label
        self.label = QLabel(self.label_text)
        self.label.setStyleSheet("""
            font-size: 11pt;
            color: #dce1ec;
            font-weight: bold;
        """)
        
        # Value label
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value_label.setStyleSheet("""
            font-size: 11pt;
            color: #568af2;
            font-weight: bold;
        """)
        
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        header_layout.addWidget(self.value_label)
        
        self.main_layout.addLayout(header_layout)
        
        # Controls layout - slider and buttons
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, self.max_value)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setStyleSheet("""
            QSlider {
                height: 22px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #343b48;
                height: 6px;
                background: #343b48;
                margin: 0px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #568af2;
                border: none;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #568af2;
                border-radius: 3px;
            }
        """)
        
        self.slider.valueChanged.connect(self._on_value_changed)
        
        # Add buttons for increment/decrement
        self.decrease_btn = QPushButton("-")
        self.decrease_btn.setFixedSize(24, 24)
        self.decrease_btn.setStyleSheet("""
            QPushButton {
                background-color: #343b48;
                color: #dce1ec;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #568af2;
            }
        """)
        self.decrease_btn.clicked.connect(self._on_decrease_clicked)
        
        self.increase_btn = QPushButton("+")
        self.increase_btn.setFixedSize(24, 24)
        self.increase_btn.setStyleSheet("""
            QPushButton {
                background-color: #343b48;
                color: #dce1ec;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #568af2;
            }
        """)
        self.increase_btn.clicked.connect(self._on_increase_clicked)
        
        controls_layout.addWidget(self.decrease_btn)
        controls_layout.addWidget(self.slider)
        controls_layout.addWidget(self.increase_btn)
        
        self.main_layout.addLayout(controls_layout)
    
    
    def _on_value_changed(self, value):
        """
        Handle when slider value changes
        
        Args:
            value (int): New value
        """
        # Update label
        self.value_label.setText(str(value))
        
        # Emit signal
        self.value_changed.emit(self._upgrade_type, value)
        
        def _on_spinbox_changed(self, value):
            """
            Handle when spinbox value changes
            
            Args:
                value (int): New value
            """
            # Update slider without triggering its signal
            self.slider.blockSignals(True)
            self.slider.setValue(value)
            self.slider.blockSignals(False)
            
            # Update label
            self.value_label.setText(str(value))
            
            # Emit signal
            self.value_changed.emit(self._upgrade_type, value)
    
    def setValue(self, value):
        """
        Set the editor value
        
        Args:
            value (int): New value
        """
        # Set slider value (will update spinbox via signal)
        self.slider.setValue(value)
    
    def value(self):
        """
        Get the current value
        
        Returns:
            int: Current value
        """
        return self.slider.value()
    
    def upgrade_type(self):
        """
        Get the upgrade type
        
        Returns:
            str: Upgrade type
        """
        return self._upgrade_type
    
    def set_upgrade_type(self, upgrade_type):
        """
        Set the upgrade type
        
        Args:
            upgrade_type (str): New upgrade type
        """
        self._upgrade_type = upgrade_type
    
    def _on_decrease_clicked(self):
        """Decrease the value by 1"""
        current_value = self.slider.value()
        if current_value > 0:
            self.slider.setValue(current_value - 1)

    def _on_increase_clicked(self):
        """Increase the value by 1"""
        current_value = self.slider.value()
        if current_value < self.max_value:
            self.slider.setValue(current_value + 1)
        
    # Define property
    upgrade_type = Property(str, upgrade_type, set_upgrade_type)