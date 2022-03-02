from abc import abstractmethod

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel
)
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt

from gui_constants import *


class Page(QWidget):

    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(PAGE_SIDES_PADDING, PAGE_TOP_PADDING, PAGE_SIDES_PADDING, 0)

    def addBox(self, hBoxLayout, spacingBelow):
        self.mainLayout.addLayout(hBoxLayout)
        self.mainLayout.addSpacing(spacingBelow)

    def addPageHeaders(self, pageName, description=None):
        self.pageHeaders = QHBoxLayout()
        self.pageName = QLabel(pageName)
        self.pageName.setStyleSheet("""
            color: {secondary};
        """.format(secondary = SECONDARY))
        font = QFont(FONT, H1_FONT)
        font.setBold(True)
        self.pageName.setFont(font)
        self.pageName.setAlignment(Qt.AlignBottom)
        self.pageHeaders.addWidget(self.pageName)

        if description:
            self.pageDescription = QLabel(description)
            self.pageDescription.setFont(QFont(FONT, SMALLEST_FONT, italic=True))
            self.pageDescription.setAlignment(Qt.AlignBottom)
            self.pageDescription.setStyleSheet("""
                color: grey;
                margin-left: 0px;
                padding-bottom: 1px;
            """)
            self.pageHeaders.addWidget(self.pageDescription)
            self.pageHeaders.addStretch()

        self.addBox(self.pageHeaders, SPACING_LARGE)

    def addScrollable(self, data, spacingBelow):
        self.initScrollable(data)
        self.colourRows()
        self.getScrollable().setStyleSheet(f"""
            background-color: white;
            border-top: 1px solid red;
            border-bottom: 1px solid red;
        """)
        self.mainLayout.addSpacing(spacingBelow)

    @abstractmethod
    def initScrollable(self, data):
        pass

    @abstractmethod
    def colourRows(self):
        pass

    @abstractmethod
    def getScrollable(self):
        pass
