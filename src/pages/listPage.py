from PySide2.QtWidgets import QScrollArea, QWidget, QVBoxLayout

from . import page


class ListPage(page.Page):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)

##    def addScrollableLayout(self, scrollableLayout):
##        self.scrollArea = QScrollArea()
##        self.scrollArea.setWidgetResizable(True)
##        self.scrollArea.setStyleSheet("""
##            background-color: white;
##            border: none;
##        """)
##        self.scrollWidget = QWidget()
##        self.scrollWidget.setLayout(scrollableLayout)
##        self.scrollArea.setWidget(self.scrollWidget)
##        self.mainLayout.addWidget(self.scrollArea)

    def initScrollable(self, hBoxLayouts):
        self.scrollLayout = QVBoxLayout()
        for i, hBoxLayout in enumerate(hBoxLayouts):
            row = QWidget()
            if i % 2 == 0:
                row.setStyleSheet(f"""
                    background-color: {SECONDARY_TINT};
                """)
            row.setLayout(hBoxLayout)
            self.scrollLayout.addWidget(row)
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(self.scrollWidget)
        self.mainLayout.addWidget(self.scrollArea)

    def getScrollable(self):
        return self.scrollArea

    def colourRows(self):
        pass
