from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QFileDialog, QListWidget, QListWidgetItem, QAbstractItemView,
    QSizePolicy, QSpacerItem, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap
import os

# Import SVG widget if available
try:
    from PySide6.QtSvg import QSvgWidget
    HAS_SVG_SUPPORT = True
except ImportError:
    HAS_SVG_SUPPORT = False

from ..widgets import ModernButton

class HomeCard(QFrame):
    """Card widget for the home page with a more compact design"""
    
    def __init__(self, title, description, icon_path=None, parent=None):
        """
        Initialize the home card
        
        Args:
            title (str): Card title
            description (str): Card description
            icon_path (str, optional): Path to icon. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Set frame style
        self.setObjectName("home_card")
        self.setStyleSheet("""
            #home_card {
                background-color: #272c36;
                border-radius: 8px;
                border: 1px solid #343b48;
            }
        """)
        
        # Set fixed height for more compact appearance
        self.setFixedHeight(140)
        
        # Card layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Icon if provided
        if icon_path:
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon_label.setFixedSize(48, 48)
                icon_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(icon_label)
        
        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #dce1ec;
        """)
        text_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 10pt;
            color: #8a95aa;
        """)
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        # Add text layout to main layout
        layout.addLayout(text_layout, 1)


class HomePage(QWidget):
    """
    Home page with save file browser and welcome message
    """
    
    # Signals
    save_selected = Signal(str)  # Emitted when a save file is selected
    refresh_requested = Signal()  # Emitted when refresh is requested
    new_game_requested = Signal()  # Signal for creating a new game
    
    def __init__(self, parent=None):
        """
        Initialize the home page
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Get app base directory for resources
        self.app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        self.icons_dir = os.path.join(self.app_dir, 'resources', 'icons')
        
        # Default save path for browsing
        self.default_save_path = self._get_default_save_path()
        
        # Set up UI
        self.setup_ui()
        
        # Save file list
        self.save_files = []
    
    def _get_default_save_path(self):
        """Get the default save path for Repo game files"""
        # Default location is in AppData\LocalLow\semiwork\Repo\saves
        if os.name == "nt":  # Windows
            app_data = os.path.expandvars("%USERPROFILE%\\AppData\\LocalLow")
            save_folder = os.path.join(app_data, "semiwork", "Repo", "saves")
            if os.path.exists(save_folder):
                return save_folder
        return ""
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Add improved logo
        main_layout.addLayout(self.create_better_svg_logo())
        
        # Subtitle
        subtitle = QLabel("A tool for editing and managing Repo game save files")
        subtitle.setStyleSheet("""
            font-size: 12pt;
            color: #8a95aa;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Save file browser section - moved up
        browser_section = QFrame()
        browser_section.setObjectName("browser_section")
        browser_section.setStyleSheet("""
            #browser_section {
                background-color: #272c36;
                border-radius: 8px;
                border: 1px solid #343b48;
            }
        """)
        
        browser_layout = QVBoxLayout(browser_section)
        browser_layout.setContentsMargins(15, 15, 15, 15)
        browser_layout.setSpacing(10)
        
        # Section title
        section_title = QLabel("Load a Save File")
        section_title.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #dce1ec;
        """)
        browser_layout.addWidget(section_title)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.browse_button = ModernButton("Browse Files", "medium", os.path.join(self.icons_dir, "open_file.svg"))
        self.browse_button.clicked.connect(self.browse_files)
        
        self.refresh_button = ModernButton("Refresh List", "medium")
        self.refresh_button.clicked.connect(self.refresh_save_list)
        
        buttons_layout.addWidget(self.browse_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()
        
        browser_layout.addLayout(buttons_layout)
        
        # Save file list
        self.save_list = QListWidget()
        self.save_list.setMinimumHeight(150)
        self.save_list.setMaximumHeight(180)
        self.save_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.save_list.setStyleSheet("""
            QListWidget {
                background-color: #2c313c;
                border: 1px solid #343b48;
                border-radius: 5px;
                color: #8a95aa;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            
            QListWidget::item:selected {
                background-color: #568af2;
                color: white;
            }
            
            QListWidget::item:hover {
                background-color: #343b48;
            }
        """)
        
        self.save_list.itemDoubleClicked.connect(self.load_selected_save)
        
        browser_layout.addWidget(self.save_list)
        
        # Load button
        load_layout = QHBoxLayout()
        load_layout.addStretch()
        
        self.load_button = ModernButton("Load Selected Save", "medium", os.path.join(self.icons_dir, "open_file.svg"))
        self.load_button.clicked.connect(self.load_selected_save)
        
        load_layout.addWidget(self.load_button)
        browser_layout.addLayout(load_layout)
        
        # Add file browser to main layout
        main_layout.addWidget(browser_section)
        
        # Cards layout - features and info in a grid for better layout
        cards_container = QFrame()
        cards_container.setObjectName("cards_container")
        cards_container.setStyleSheet("""
            #cards_container {
                background-color: transparent;
            }
        """)
        
        cards_layout = QGridLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(15)
        
        # Create feature cards
        cards = [
            ("Edit Game Data", "Modify player stats, upgrades, items, and run stats in a few clicks.", 
            os.path.join(self.icons_dir, "player.svg")),
            ("Steam Integration", "Automatically fetches player avatars for a better visual experience.", 
            os.path.join(self.icons_dir, "items.svg")),
            ("Safe Backups", "Automatically creates backups of your save files before making changes.", 
            os.path.join(self.icons_dir, "save_file.svg"))
        ]
        
        # Add new game button
        self.new_game_button = ModernButton("Create New Game", "medium")
        buttons_layout.addWidget(self.new_game_button)
        self.new_game_button.clicked.connect(self.on_new_game_clicked)
        
        # Add cards in a row
        for i, (title, description, icon) in enumerate(cards):
            card = HomeCard(title, description, icon)
            cards_layout.addWidget(card, 0, i)
        
        main_layout.addWidget(cards_container)
        
        # Add stretch to push content up
        main_layout.addStretch()
    
    def on_new_game_clicked(self):
        """Signal to create a new game"""
        # Emit a signal to the main window
        self.new_game_requested.emit()

    def create_better_svg_logo(self):
        """Create a better quality SVG logo"""
        # Create a layout for the logo
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        logo_path = os.path.join(self.icons_dir, "reposavelogo.svg")
        
        if os.path.exists(logo_path):
            try:
                # Check if QtSvg is available
                from PySide6.QtSvg import QSvgWidget
                
                # Create SVG widget
                logo_widget = QSvgWidget(logo_path)
                
                # Set a fixed size that's larger to avoid scaling issues
                logo_widget.setFixedSize(280, 70)
                
                # Add to layout
                logo_layout.addWidget(logo_widget)
                
                return logo_layout
                
            except ImportError:
                # If QtSvg not available, use QPixmap
                pass
                
        # Fallback to QPixmap or text
        try:
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # Create a larger pixmap first, then scale down for better quality
                scaled_pixmap = pixmap.scaled(280, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_layout.addWidget(logo_label)
                return logo_layout
        except:
            pass
        
        # Final fallback to text
        title = QLabel("Repo Save Modifier")
        title.setStyleSheet("""
            font-size: 28pt;
            font-weight: bold;
            color: #dce1ec;
        """)
        title.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(title)
        
        return logo_layout


    def populate_save_list(self, save_files):
        """
        Populate the list with save files
        
        Args:
            save_files (list): List of tuples (display_name, save_folder_path, full_save_file_path)
        """
        self.save_files = save_files
        self.save_list.clear()
        
        if not save_files:
            item = QListWidgetItem("No save files found")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.save_list.addItem(item)
            return
        
        for display_name, _, full_path in save_files:
            # Create list item with display name
            item = QListWidgetItem(QIcon(os.path.join(self.icons_dir, "save_file.svg")), display_name)
            item.setData(Qt.UserRole, full_path)  # Store full path to ES3 file
            self.save_list.addItem(item)
    
    def browse_files(self):
        """Open file dialog to browse for save files"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Repo Save Files (*.Es3)")
        
        # Set the default directory to the Repo save folder
        if self.default_save_path and os.path.exists(self.default_save_path):
            file_dialog.setDirectory(self.default_save_path)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # Emit signal with selected file
                self.save_selected.emit(selected_files[0])
    
    def refresh_save_list(self):
        """
        Refresh the save file list
        
        This method is now connected to the MainWindow's refresh_save_list method
        which will populate the list via populate_save_list
        """
        # The actual refresh is now handled by the MainWindow
        self.refresh_requested.emit()
    
    def load_selected_save(self):
        """Load the selected save file"""
        current_item = self.save_list.currentItem()
        if current_item:
            file_path = current_item.data(Qt.UserRole)
            if file_path:
                # Emit signal with selected file
                self.save_selected.emit(file_path)