from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, 
    QSpinBox, QLineEdit, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

class ValueEditor(QFrame):
    """
    Widget for editing numeric or text values with a label.
    """
    
    # Signal emitted when the value changes
    value_changed = Signal(str, object)  # key, value
    
    def __init__(self, key, label=None, value=0, value_type="int", 
                 min_value=0, max_value=1000000, parent=None):
        """
        Args:
            key (str): Unique identifier for this editor
            label (str, optional): Display label. If None or empty, no label is shown.
            value (object, optional): Initial value. Defaults to 0.
            value_type (str, optional): "int", "float", or "text". Defaults to "int".
            min_value (int, optional): Minimum value for numeric types. Defaults to 0.
            max_value (int, optional): Maximum value for numeric types. Defaults to 1000000.
        """
        super().__init__(parent)
        
        self.key = key
        self.label_text = label if label else ""  # Convert None -> empty string
        self.value_type = value_type
        self.min_value = min_value
        self.max_value = max_value
        
        # Set up UI
        self.setup_ui()
        
        # Set initial value
        self.set_value(value)
    
    def setup_ui(self):
        """Set up the UI components."""
        self.setObjectName("value_editor")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            #value_editor {
                background-color: #272c36;
                border-radius: 6px;
                border: 1px solid #343b48;
                padding: 0px;
                min-height: 36px;
                max-height: 36px;
            }
        """)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 0, 4, 0)  # Reduced vertical margins
        self.main_layout.setSpacing(4)

        # Only create a label if label_text is not empty
        if self.label_text.strip():
            self.label = QLabel(self.label_text)
            self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.label.setStyleSheet("""
                font-size: 10pt;
                color: #dce1ec;
            """)
            self.main_layout.addWidget(self.label)

        # Create the appropriate editor
        if self.value_type in ["int", "float"]:
            self._create_numeric_editor()
        else:
            self._create_text_editor()
    
    def _create_numeric_editor(self):
        """Create the editor for numeric values with buttons on both sides."""
        # Create a horizontal container layout
        container = QFrame()
        container.setObjectName("numeric_container")
        container.setFixedHeight(36)  # Match the height of the ValueEditor frame
        container.setStyleSheet("""
            #numeric_container {
                background-color: transparent;
            }
        """)
        
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)
        
        # Reduce the button size to fit better
        button_size = 28
        
        # Decrement button on the left
        self.decrement_button = QPushButton("-")
        self.decrement_button.setFixedSize(button_size, button_size)
        self.decrement_button.setCursor(Qt.PointingHandCursor)
        self.decrement_button.clicked.connect(self._decrement_value)
        self.decrement_button.setStyleSheet("""
            QPushButton {
                background-color: #343b48;
                color: #dce1ec;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #568af2;
            }
        """)
        
        # Spinbox in the middle
        self.value_input = QSpinBox()
        self.value_input.setButtonSymbols(QSpinBox.NoButtons)
        self.value_input.setRange(self.min_value, self.max_value)
        self.value_input.setAlignment(Qt.AlignCenter)
        self.value_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.value_input.setMinimumWidth(60)
        self.value_input.setFixedHeight(28)
        self.value_input.setStyleSheet("""
            QSpinBox {
                background-color: #2c313c;
                color: #dce1ec;
                border: 1px solid #343b48;
                border-radius: 4px;
                padding: 2px;
                font-size: 10pt;
            }
            QSpinBox:focus {
                border: 1px solid #568af2;
            }
        """)
        self.value_input.valueChanged.connect(self._on_value_changed)
        
        # Increment button on the right
        self.increment_button = QPushButton("+")
        self.increment_button.setFixedSize(button_size, button_size)
        self.increment_button.setCursor(Qt.PointingHandCursor)
        self.increment_button.clicked.connect(self._increment_value)
        self.increment_button.setStyleSheet("""
            QPushButton {
                background-color: #343b48;
                color: #dce1ec;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #568af2;
            }
        """)
        
        # Add widgets to container layout
        container_layout.addWidget(self.decrement_button)
        container_layout.addWidget(self.value_input)
        container_layout.addWidget(self.increment_button)
        
        # Add the container to the main layout
        self.main_layout.addWidget(container)
    
    def _create_text_editor(self):
        """Create the editor for text values."""
        self.value_input = QLineEdit()
        self.value_input.setAlignment(Qt.AlignLeft)
        self.value_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.value_input.setMinimumWidth(120)
        self.value_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c313c;
                color: #dce1ec;
                border: 1px solid #343b48;
                border-radius: 4px;
                padding: 2px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #568af2;
            }
        """)
        
        self.value_input.textChanged.connect(self._on_text_changed)
        self.main_layout.addWidget(self.value_input)
    
    def set_value(self, value):
        """
        Set the editor value.
        """
        if self.value_type in ["int", "float"]:
            try:
                numeric_value = float(value) if self.value_type == "float" else int(value)
                self.value_input.setValue(numeric_value)
            except (ValueError, TypeError):
                self.value_input.setValue(self.min_value)
        else:
            self.value_input.setText(str(value))
    
    def get_value(self):
        """
        Get the current value.
        """
        if self.value_type in ["int", "float"]:
            return self.value_input.value()
        else:
            return self.value_input.text()
    
    def set_range(self, min_value, max_value):
        """
        Set the allowed range for numeric values.
        """
        if self.value_type in ["int", "float"] and hasattr(self, 'value_input'):
            self.min_value = min_value
            self.max_value = max_value
            self.value_input.setRange(min_value, max_value)
    
    def _increment_value(self):
        """Increment the value by one step."""
        if self.value_type in ["int", "float"] and hasattr(self, 'value_input'):
            current_value = self.value_input.value()
            step = 0.1 if self.value_type == "float" else 1
            self.value_input.setValue(min(current_value + step, self.max_value))
    
    def _decrement_value(self):
        """Decrement the value by one step."""
        if self.value_type in ["int", "float"] and hasattr(self, 'value_input'):
            current_value = self.value_input.value()
            step = 0.1 if self.value_type == "float" else 1
            self.value_input.setValue(max(current_value - step, self.min_value))
    
    def _on_value_changed(self, value):
        """
        Handle when the numeric value changes.
        """
        self.value_changed.emit(self.key, value)
    
    def _on_text_changed(self, text):
        """
        Handle when the text value changes.
        """
        self.value_changed.emit(self.key, text)
