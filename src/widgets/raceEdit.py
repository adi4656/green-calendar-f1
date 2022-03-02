from PySide2.QtWidgets import QComboBox, QCompleter
from PySide2.QtCore import Qt, QStringListModel
from PySide2.QtGui import QFontMetrics, QFont

from gui_constants import FONT, H2_FONT, SECONDARY_TINT


class RaceEdit(QComboBox):
    """Widget for entering races."""

    def __init__(self, races, placeholderText):
        super().__init__()
        self.model = QStringListModel(races)
        self.setModel(self.model)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.completer = QCompleter(self.model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCurrentIndex(-1)
        self.lineEdit().setPlaceholderText(placeholderText)

        self.setStyleSheet(f"""
            QComboBox{{
                width: 420px;
                height: {QFontMetrics(QFont(FONT, H2_FONT)).height()}px;
                border: none;
                font-family: {FONT};
                font-size: {H2_FONT}px;
            }}
        """)
        self.lineEdit().setAlignment(Qt.AlignBottom)
        self.lineEdit().setStyleSheet(f"""
            border-bottom: 1px solid lightGray;
            background-color: {SECONDARY_TINT};
        """)
