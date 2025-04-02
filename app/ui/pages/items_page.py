from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QGroupBox, QSizePolicy,
    QSpacerItem, QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..widgets import ModernButton, ModernTable, ValueEditor

class ItemsPage(QWidget):
    """
    Page for editing game items with categorized tabs
    """
    
    # Signals
    item_purchased_changed = Signal(str, int)  # item_name, quantity
    item_upgrade_changed = Signal(str, int)  # item_name, quantity
    
    def __init__(self, parent=None):
        """
        Initialize the items page
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Store item editors
        self.item_editors = {}  # {item_name: ValueEditor}
        self.upgrade_editors = {}  # {item_name: ValueEditor}
        
        # Store original values for reset
        self.original_items = None
        
        # Item categories
        self.categories = {
            "utility": {
                "title": "Utility Items",
                "items": [
                    "Item Cart Medium", "Item Cart Small", "Item Drone Battery", "Item Drone Feather",
                    "Item Drone Indestructible", "Item Drone Torque", "Item Drone Zero Gravity",
                    "Item Extraction Tracker", "Item Orb Zero Gravity", "Item Power Crystal",
                    "Item Valuable Tracker"  # Moved to utility items
                ]
            },
            "throwable": {
                "title": "Throwable Items",
                "items": [
                    "Item Grenade Duct Taped", "Item Grenade Explosive", "Item Grenade Human", 
                    "Item Grenade Shockwave", "Item Grenade Stun", "Item Rubber Duck"
                ]
            },
            "weapons": {
                "title": "Weapons",
                "items": [
                    "Item Gun Handgun", "Item Gun Shotgun", "Item Gun Tranq", 
                    "Item Melee Baseball Bat", "Item Melee Frying Pan",
                    "Item Melee Inflatable Hammer", "Item Melee Sledge Hammer", "Item Melee Sword"
                ]
            },
            "mines": {
                "title": "Mines",
                "items": [
                    "Item Mine Explosive", "Item Mine Shockwave", "Item Mine Stun"
                ]
            },
            "upgrades": {
                "title": "Upgrades + Health",
                "items": [
                    "Item Health Pack Large", "Item Health Pack Medium", "Item Health Pack Small",
                    "Item Upgrade Map Player Count", "Item Upgrade Player Energy", 
                    "Item Upgrade Player Extra Jump", "Item Upgrade Player Grab Range",
                    "Item Upgrade Player Grab Strength", "Item Upgrade Player Health", 
                    "Item Upgrade Player Sprint Speed", "Item Upgrade Player Tumble Launch"
                    # Removed Item Valuable Tracker
                ],
                "upgrades": [
                    "Item Upgrade Map Player Count", "Item Upgrade Player Energy", 
                    "Item Upgrade Player Extra Jump", "Item Upgrade Player Grab Range",
                    "Item Upgrade Player Grab Strength", "Item Upgrade Player Health", 
                    "Item Upgrade Player Sprint Speed", "Item Upgrade Player Tumble Launch"
                    # Removed Item Valuable Tracker
                ]
            }
        }
        
        # Set up UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Page title
        title = QLabel("Items Editor")
        title.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: #dce1ec;
        """)
        main_layout.addWidget(title)
        
        # Description
        description = QLabel(
            "Edit items and upgrades purchased in the game. Items are organized by category."
        )
        description.setStyleSheet("""
            font-size: 11pt;
            color: #8a95aa;
        """)
        main_layout.addWidget(description)
        
        # Tab widget for different item sections
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
        
        # Create category tabs
        self.category_tabs = {}
        for category_key, category_data in self.categories.items():
            tab = self.create_category_tab(category_key, category_data["title"])
            self.category_tabs[category_key] = tab
            self.tab_widget.addTab(tab, category_data["title"])
        
        main_layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.reset_button = ModernButton("Reset Changes", "medium")
        self.reset_button.clicked.connect(self.reset_changes)
        
        buttons_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(buttons_layout)
    
    def create_category_tab(self, category_key, category_title):
        """
        Create a tab for an item category
        
        Args:
            category_key (str): Category key
            category_title (str): Category display title
            
        Returns:
            QWidget: Tab widget
        """
        # Create widget
        category_widget = QWidget()
        
        # Create scroll area for items
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
        category_layout = QVBoxLayout(scroll_content)
        category_layout.setContentsMargins(15, 15, 15, 15)
        category_layout.setSpacing(15)
        
        # Add note about item updates
        note_label = QLabel(
            "Note: Changing item quantities will update both the current inventory "
            "and the total items purchased."
        )
        note_label.setStyleSheet("""
            font-style: italic;
            color: #8a95aa;
            padding: 10px;
            background-color: #2c313c;
            border-radius: 5px;
        """)
        note_label.setWordWrap(True)
        category_layout.addWidget(note_label)
        
        # Empty state placeholder - ONLY for non-upgrades tabs
        # For upgrades tab, we'll handle this differently
        if category_key != "upgrades":
            placeholder = QLabel(f"No {category_title.lower()} found in save file.")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("""
                font-size: 14pt;
                color: #8a95aa;
                padding: 40px;
            """)
            placeholder.setObjectName(f"{category_key}_placeholder")
            category_layout.addWidget(placeholder)
            
            # Store placeholder reference
            setattr(self, f"{category_key}_placeholder", placeholder)
        else:
            # For upgrades tab, we'll create a placeholder but keep it hidden initially
            placeholder = QLabel(f"No {category_title.lower()} found in save file.")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("""
                font-size: 14pt;
                color: #8a95aa;
                padding: 40px;
            """)
            placeholder.setObjectName(f"{category_key}_placeholder")
            placeholder.setVisible(False)  # Initially hidden for upgrades tab
            category_layout.addWidget(placeholder)
            
            # Store placeholder reference
            setattr(self, f"{category_key}_placeholder", placeholder)
        
        # If this is the upgrades tab, add a section for upgrades
        if category_key == "upgrades":
            # Add section title for upgrades
            '''upgrade_title = QLabel("Upgrade Levels")
            upgrade_title.setStyleSheet("""
                font-size: 16pt;
                font-weight: bold;
                color: #dce1ec;
                margin-top: 20px;
            """)
            category_layout.addWidget(upgrade_title)
            
            # Add note about upgrade effects
            upgrade_note = QLabel(
                "These upgrades affect various player abilities. "
                "Changing these values will update the upgrades purchased."
            )
            upgrade_note.setStyleSheet("""
                font-style: italic;
                color: #8a95aa;
                padding: 10px;
                background-color: #2c313c;
                border-radius: 5px;
            """)
            upgrade_note.setWordWrap(True)
            category_layout.addWidget(upgrade_note)'''
            
            # Create a separate layout for the upgrade editors
            self.upgrades_editors_layout = QVBoxLayout()
            category_layout.addLayout(self.upgrades_editors_layout)
            
            # Add empty state for upgrades - but initially hidden
            self.upgrades_placeholder = QLabel("No upgrade items found in save file.")
            self.upgrades_placeholder.setAlignment(Qt.AlignCenter)
            self.upgrades_placeholder.setStyleSheet("""
                font-size: 14pt;
                color: #8a95aa;
                padding: 20px;
            """)
            self.upgrades_placeholder.setVisible(False)  # Initially hidden
            self.upgrades_editors_layout.addWidget(self.upgrades_placeholder)
        
        # Add spacer at the end
        category_layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(scroll_content)
        
        # Main layout for the tab
        tab_layout = QVBoxLayout(category_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        
        # Store layout reference
        setattr(self, f"{category_key}_layout", category_layout)
        
        return category_widget
    
    def display_items(self, items):
        """
        Display items from a game save, organized by category
        
        Args:
            items (dict): Items dictionary from GameSave
        """
        # Store original items for reset
        self.original_items = {
            "purchased": dict(items.get("purchased", {})),
            "purchasedTotal": dict(items.get("purchasedTotal", {})),
            "upgradesPurchased": dict(items.get("upgradesPurchased", {}))
        }
        
        # Clear existing editors
        self.clear_items()
        
        # Get purchased items
        purchased_items = items.get("purchased", {})
        
        # Check if we have any items at all
        if not purchased_items:
            # Show placeholders on all tabs
            for category_key in self.categories:
                placeholder = getattr(self, f"{category_key}_placeholder")
                placeholder.setVisible(True)
            return
        
        # Process each category
        for category_key, category_data in self.categories.items():
            # Get the layout
            layout = getattr(self, f"{category_key}_layout")
            
            # Get the placeholder
            placeholder = getattr(self, f"{category_key}_placeholder")
            
            # Filter items for this category (excluding upgrades in the upgrades tab)
            category_items = {
                item_name: quantity 
                for item_name, quantity in purchased_items.items() 
                if item_name in category_data["items"] and (
                    # For upgrades tab, exclude items that are upgrades (they'll be shown in the upgrades section)
                    category_key != "upgrades" or 
                    item_name not in category_data.get("upgrades", [])
                )
            }
            
            # For the upgrades tab, we need to check if there are any items OR upgrades
            if category_key == "upgrades":
                has_upgrades = False
                
                # Check if there are any upgrades in the upgradesPurchased dictionary
                if "upgradesPurchased" in items:
                    for upgrade_name in category_data.get("upgrades", []):
                        if upgrade_name in items["upgradesPurchased"]:
                            has_upgrades = True
                            break
                            
                # If we have either regular items or upgrades in this tab
                if category_items or has_upgrades:
                    placeholder.setVisible(False)
                else:
                    placeholder.setVisible(True)
            else:
                # For other tabs, just check if there are any items
                if not category_items:
                    placeholder.setVisible(True)
                    continue
                else:
                    placeholder.setVisible(False)
            
            # Create editors for each item in this category
            for item_name, quantity in category_items.items():
                # Create editor
                editor = ValueEditor(
                    key=f"item_{item_name}",
                    label=self._format_item_name(item_name),
                    value=quantity,
                    value_type="int",
                    min_value=0,
                    max_value=9999
                )
                editor.value_changed.connect(lambda k, v, name=item_name: self.on_item_changed(name, v))
                
                # Add to layout before the stretch
                layout.insertWidget(layout.count() - 1, editor)
                self.item_editors[item_name] = editor
        
        # Now handle the upgrades
        self.display_upgrades(items)
    
    def _format_item_name(self, item_name):
        """
        Format item name for display
        
        Args:
            item_name (str): Item name from save file
            
        Returns:
            str: Formatted name
        """
        # Remove "Item " prefix
        name = item_name.replace("Item ", "")
        
        # Replace underscores with spaces
        name = name.replace("_", " ")
        
        return name
    
    def display_upgrades(self, upgrades):
        """
        Display upgrade items from a game save
        
        Args:
            upgrades (dict): Upgrades dictionary from GameSave
        """
        # Clear existing upgrade editors
        self.clear_upgrades()
        
        # Get upgrades
        upgrade_items = upgrades.get("upgradesPurchased", {})
        
        # Check for both the layout and the placeholder
        if not hasattr(self, 'upgrades_editors_layout'):
            return
            
        # Explicitly hide the main placeholder in the upgrades tab
        # This is the most important line to fix the issue
        if hasattr(self, 'upgrades_placeholder'):
            self.upgrades_placeholder.setVisible(False)
            
        # Also explicitly hide the category placeholder
        if hasattr(self, "upgrades_placeholder"):
            placeholder = getattr(self, "upgrades_placeholder")
            placeholder.setVisible(False)
        
        # No upgrades - just return (but keep placeholder hidden if we have items)
        if not upgrade_items:
            return
        
        # Create editors for each upgrade
        # Get the list of upgrade items from the category definition
        upgrade_item_names = self.categories["upgrades"].get("upgrades", [])
        
        for item_name in upgrade_item_names:
            if item_name in upgrade_items:
                # Create editor
                editor = ValueEditor(
                    key=f"upgrade_{item_name}",
                    label=self._format_item_name(item_name),
                    value=upgrade_items[item_name],
                    value_type="int",
                    min_value=0,
                    max_value=10
                )
                editor.value_changed.connect(lambda k, v, name=item_name: self.on_upgrade_changed(name, v))
                
                # Add to the upgrades layout
                self.upgrades_editors_layout.insertWidget(self.upgrades_editors_layout.count() - 1, editor)
                self.upgrade_editors[item_name] = editor
    
    def clear_items(self):
        """Clear all item editors"""
        # Remove all editors
        for item_name, editor in list(self.item_editors.items()):
            # Remove from layout
            for category_key in self.categories:
                layout = getattr(self, f"{category_key}_layout")
                try:
                    layout.removeWidget(editor)
                except:
                    pass  # Widget wasn't in this layout
            
            # Delete widget
            editor.deleteLater()
        
        self.item_editors.clear()
        
        # Show all placeholders
        for category_key in self.categories:
            placeholder = getattr(self, f"{category_key}_placeholder")
            placeholder.setVisible(True)
    
    def clear_upgrades(self):
        """Clear all upgrade editors"""
        # Remove all upgrade editors
        for item_name, editor in list(self.upgrade_editors.items()):
            if hasattr(self, 'upgrades_editors_layout'):
                try:
                    self.upgrades_editors_layout.removeWidget(editor)
                except:
                    pass  # Widget wasn't in this layout
            editor.deleteLater()
        
        self.upgrade_editors.clear()
        
        # Show placeholder if it exists
        if hasattr(self, 'upgrades_placeholder'):
            self.upgrades_placeholder.setVisible(True)
    
    def on_item_changed(self, item_name, quantity):
        """
        Handle when an item quantity changes
        
        Args:
            item_name (str): Item name
            quantity (int): New quantity
        """
        self.item_purchased_changed.emit(item_name, quantity)
    
    def on_upgrade_changed(self, item_name, quantity):
        """
        Handle when an upgrade quantity changes
        
        Args:
            item_name (str): Upgrade item name
            quantity (int): New quantity
        """
        self.item_upgrade_changed.emit(item_name, quantity)
    
    def update_item_quantity(self, item_name, quantity):
        """
        Update an item's quantity in the UI
        
        Args:
            item_name (str): Item name
            quantity (int): New quantity
        """
        if item_name in self.item_editors:
            # Update without emitting signals
            self.item_editors[item_name].blockSignals(True)
            self.item_editors[item_name].set_value(quantity)
            self.item_editors[item_name].blockSignals(False)
    
    def update_upgrade_quantity(self, item_name, quantity):
        """
        Update an upgrade's quantity in the UI
        
        Args:
            item_name (str): Upgrade item name
            quantity (int): New quantity
        """
        if item_name in self.upgrade_editors:
            # Update without emitting signals
            self.upgrade_editors[item_name].blockSignals(True)
            self.upgrade_editors[item_name].set_value(quantity)
            self.upgrade_editors[item_name].blockSignals(False)
    
    def reset_changes(self):
        """
        Reset all changes to original values for the items page only
        """
        if hasattr(self, 'original_items') and self.original_items:
            # Reset regular items
            for item_name, editor in self.item_editors.items():
                if item_name in self.original_items.get("purchased", {}):
                    original_value = self.original_items["purchased"][item_name]
                    editor.set_value(original_value)
                    # Emit the signal to update the model
                    self.on_item_changed(item_name, original_value)
            
            # Reset upgrades
            for item_name, editor in self.upgrade_editors.items():
                if item_name in self.original_items.get("upgradesPurchased", {}):
                    original_value = self.original_items["upgradesPurchased"][item_name]
                    editor.set_value(original_value)
                    # Emit the signal to update the model
                    self.on_upgrade_changed(item_name, original_value)
            
            # Show success message
            QMessageBox.information(self, "Reset Complete", "Item values have been reset to their original values.")
        else:
            QMessageBox.warning(self, "Reset Failed", "Original item values are not available.")