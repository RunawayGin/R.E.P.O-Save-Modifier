from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QWidget, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

class ModernTable(QTableWidget):
    """
    Enhanced table widget with modern styling and additional features
    """
    
    # Signal for when data changes
    data_changed = Signal(int, int, object)
    
    def __init__(self, rows=0, columns=0):
        """
        Initialize the modern table
        
        Args:
            rows (int, optional): Initial number of rows. Defaults to 0.
            columns (int, optional): Initial number of columns. Defaults to 0.
        """
        super().__init__(rows, columns)
        
        # Set up table properties
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        
        # Set up column stretching
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(36)
        
        # Customize appearance
        self.setShowGrid(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #272c36;
                alternate-background-color: #2c313c;
                border: 1px solid #343b48;
                border-radius: 5px;
                gridline-color: #343b48;
                color: #8a95aa;
            }
            
            QTableWidget::item {
                padding: 5px;
                border-color: #343b48;
            }
            
            QTableWidget::item:selected {
                background-color: #568af2;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #2c313c;
                padding: 5px;
                border: 1px solid #343b48;
                color: #dce1ec;
                font-weight: bold;
            }
        """)
        
        # Connect signals
        self.cellChanged.connect(self._on_cell_changed)
    
    def _on_cell_changed(self, row, column):
        """
        Handle when a cell's data changes
        
        Args:
            row (int): Row index
            column (int): Column index
        """
        item = self.item(row, column)
        if item:
            self.data_changed.emit(row, column, item.text())
    
    def set_headers(self, headers):
        """
        Set table headers
        
        Args:
            headers (list): List of header strings
        """
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
    
    def set_data(self, data):
        """
        Set table data
        
        Args:
            data (list): List of rows, where each row is a list of cell values
        """
        # Clear table
        self.clearContents()
        
        # Set row count
        self.setRowCount(len(data))
        
        # Add data
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                self.setItem(row_idx, col_idx, item)
    
    def get_data(self):
        """
        Get the table data
        
        Returns:
            list: List of rows, where each row is a list of cell values
        """
        data = []
        for row in range(self.rowCount()):
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            data.append(row_data)
        return data
    
    def add_row(self, row_data=None):
        """
        Add a row to the table
        
        Args:
            row_data (list, optional): Row data. Defaults to None.
        """
        current_row_count = self.rowCount()
        self.setRowCount(current_row_count + 1)
        
        if row_data:
            for col, data in enumerate(row_data):
                if col < self.columnCount():
                    item = QTableWidgetItem(str(data))
                    self.setItem(current_row_count, col, item)
    
    def remove_row(self, row=None):
        """
        Remove a row from the table
        
        Args:
            row (int, optional): Row index. If None, removes the selected row or the last row. Defaults to None.
        """
        if row is None:
            row = self.currentRow()
            if row < 0 and self.rowCount() > 0:
                row = self.rowCount() - 1
        
        if row >= 0 and row < self.rowCount():
            self.removeRow(row)
    
    def clear_selection(self):
        """Clear the current selection"""
        self.clearSelection()
        self.setCurrentCell(-1, -1)
    
    def highlight_cell(self, row, column, color="#568af2"):
        """
        Highlight a specific cell
        
        Args:
            row (int): Row index
            column (int): Column index
            color (str, optional): Highlight color. Defaults to "#568af2".
        """
        item = self.item(row, column)
        if item:
            item.setBackground(QBrush(QColor(color)))
