# IMPORTS
#
# Standard system imports
import sys
import os
import json
import pathlib
from math import sqrt

#
# Related third party imports
from PySide2.QtWidgets import (
    QMainWindow,
    QToolBar,
    QApplication,
    QButtonGroup,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QStackedWidget,
    QSizePolicy,
    QFrame,
    QTabWidget,
    QHBoxLayout,
    QLineEdit,
    QCompleter,
    QComboBox,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QScrollArea
)
from PySide2.QtCore import (
    Qt,
    QSize,
    QPoint,
    QObject,
    Signal,
    Slot,
    QPersistentModelIndex,
    QEvent,
    QModelIndex,
    QStringListModel,
)
from PySide2.QtGui import (
    QIcon,
    QFont,
    QPixmap,
    QFontMetrics,
    QBrush,
    QColor,
    QPainter,
    QPen,
    QBrush,
    QImage,
)

#
# Local application/library specific imports
RESOURCES_PATH = pathlib.Path.cwd().parent / "images"
sys.path.append(str(RESOURCES_PATH))
import resources
import file_constants
import file_formatting
from gui_constants import *

from pages.page import Page as Page
from pages.listPage import ListPage as ListPage
from pages.tablePage import TablePage as TablePage

from widgets.myToolButton import MyToolButton as MyToolButton
from widgets.raceEdit import RaceEdit as RaceEdit

def convertImageColor(image, rRange, gRange, bRange, targetColor):
    res = image.convertToFormat(QImage.Format_ARGB32)
    for x in range(res.width()):
        for y in range(res.height()):
            origColor = res.pixelColor(x, y)
            if origColor.alpha() == 255:
                if (origColor.red() in rRange and origColor.green() in gRange
                        and origColor.blue() in bRange):
                    res.setPixelColor(x, y, targetColor)
    return res


class TableWidget(QTableWidget):

    cellExited = Signal(int, int)

    def __init__(self, table_data, columns):
        super().__init__()

        self.ICON_DIMENSION = 15
        self.CELL_PADDING = 10
        self.NUM_ACTIONS = 2
        self.ITEM_FLAG = Qt.NoItemFlags

        self.createArrowIcons()
        self.createBinIcons()

        self.setRowCount(len(table_data))
        self.setColumnCount(self.NUM_ACTIONS + 1 + len(columns))
        self.setIconSize(QSize(self.ICON_DIMENSION, self.ICON_DIMENSION))

        self.populateHeaders(table_data, columns)
        self.populateActions()
        self.populateData(table_data, columns)

        self._last_index = QPersistentModelIndex()
        self.viewport().installEventFilter(self)
        self.cellClicked.connect(self.tableClickAction)

    def getData(self):
        table_data = {}
        idIndex = self.NUM_ACTIONS  # Assuming id index is leftmost column after actions
        for row in range(self.rowCount()):
            rowData = []
            for col in range(self.columnCount() - self.NUM_ACTIONS):
                col += self.NUM_ACTIONS
                if col != idIndex:
                    rowData.append(self.item(row, col).text())
            table_data[self.item(row, idIndex).text()] = rowData
        return table_data

    def eventFilter(self, widget, event):
        if widget is self.viewport():
            index = self._last_index
            if event.type() == QEvent.MouseMove:
                index = self.indexAt(event.pos())
            elif event.type() == QEvent.Leave:
                index = QModelIndex()
            if index != self._last_index:
                row = self._last_index.row()
                column = self._last_index.column()
                self.cellExited.emit(row, column)
                self._last_index = QPersistentModelIndex(index)
        return QTableWidget.eventFilter(self, widget, event)

    def createBinIcons(self):
        blackBinImage = QImage(BIN_ICON).convertToFormat(
            QImage.Format_Indexed8
        )  # Only black/white and alpha used, so use fewest possible colours
        redBinImage = convertImageColor(blackBinImage, range(1), range(1),
                                        range(1), QColor("red"))

        self.BLACK_BIN, self.RED_BIN = (QIcon(), QIcon())
        self.BLACK_BIN.addPixmap(QPixmap.fromImage(blackBinImage),
                                 QIcon.Disabled)
        self.RED_BIN.addPixmap(QPixmap.fromImage(redBinImage), QIcon.Disabled)

    def createArrowIcons(self):
        arrowPixmaps = []
        SORT_ICON_DIMENSION = 100
        for i in range(3):
            newPixmap = QPixmap(SORT_ICON_DIMENSION, SORT_ICON_DIMENSION)
            newPixmap.fill()
            newPixmap = self.paintSortArrow(newPixmap, i, SORT_ICON_DIMENSION)
            arrowPixmaps.append(newPixmap)
        self.DOWN_ARROW, self.UP_ARROW, self.COMBINED_ARROW = [
            QIcon(arrowPixmaps[i]) for i in [0, 1, 2]
        ]

    def paintSortArrow(self, pixmap, arrowType, SORT_ICON_DIMENSION):
        """Paints arrow described by arrowType onto pixmap.
        arrowType is 0 for down arrow, 1 for up arrow, 2 for both."""

        arrowPadding = 10
        HALF_SORT_ICON_DIMENSION = int(SORT_ICON_DIMENSION / 2)
        pixmap = pixmap.scaled(SORT_ICON_DIMENSION, SORT_ICON_DIMENSION)
        painter = QPainter()
        painter.begin(pixmap)
        arrowColor = "lightGray"
        painter.setPen(QColor(arrowColor))
        painter.setBrush(QColor(arrowColor))
        pointsUp = []
        pointsDown = []
        if arrowType == 0 or arrowType == 2:  # down arrow
            pointsDown = [
                QPoint(2 * arrowPadding,
                       HALF_SORT_ICON_DIMENSION + arrowPadding),
                QPoint(
                    SORT_ICON_DIMENSION - 2 * arrowPadding,
                    HALF_SORT_ICON_DIMENSION + arrowPadding,
                ),
                QPoint(HALF_SORT_ICON_DIMENSION,
                       SORT_ICON_DIMENSION - arrowPadding),
            ]
            pointsDown = [
                QPoint(0, HALF_SORT_ICON_DIMENSION + arrowPadding),
                QPoint(
                    SORT_ICON_DIMENSION - 4 * arrowPadding,
                    HALF_SORT_ICON_DIMENSION + arrowPadding,
                ),
                QPoint(
                    HALF_SORT_ICON_DIMENSION - 2 * arrowPadding,
                    SORT_ICON_DIMENSION - arrowPadding,
                ),
            ]
        if arrowType == 1 or arrowType == 2:  # up arrow
            pointsUp = [
                QPoint(0, HALF_SORT_ICON_DIMENSION - arrowPadding),
                QPoint(
                    SORT_ICON_DIMENSION - 4 * arrowPadding,
                    HALF_SORT_ICON_DIMENSION - arrowPadding,
                ),
                QPoint(HALF_SORT_ICON_DIMENSION - 2 * arrowPadding,
                       arrowPadding),
            ]
        painter.drawPolygon(pointsDown)
        painter.drawPolygon(pointsUp)
        painter.end()
        return pixmap

    def populateActions(self):
        for rowNum in range(self.rowCount()):
            pencilItem = QTableWidgetItem(QIcon(PENCIL_ICON), "")
            pencilItem.setFlags(self.ITEM_FLAG)
            self.setItem(rowNum, 0, pencilItem)
            self.setColumnWidth(0, self.ICON_DIMENSION + self.CELL_PADDING)

            deleteItem = QTableWidgetItem(self.BLACK_BIN, "")
            deleteItem.setFlags(self.ITEM_FLAG)
            self.setItem(rowNum, 1, deleteItem)
            self.setColumnWidth(1, self.ICON_DIMENSION + self.CELL_PADDING)

        self.setMouseTracking(True)
        self.cellEntered.connect(self.hoverAction)
        self.cellExited.connect(self.cellExitAction)

    def populateHeaders(self, table_data, columns):
        for colIndex in range(self.NUM_ACTIONS):
            self.changeHeaderItem(colIndex, None, "")
        for colIndex, colName in enumerate(["Shortname"] + columns):
            self.changeHeaderItem(colIndex + self.NUM_ACTIONS,
                                  self.COMBINED_ARROW, colName)

        self.horizontalHeader().sectionClicked.connect(self.sortTable)
        self.sortByColumn(
            columns.index("Leg") + self.NUM_ACTIONS, Qt.DescendingOrder)
        self.order = (
            Qt.AscendingOrder
        )  # Do not use sort indicator; state is not kept through multiple slots
        self.sortedCol = columns.index("Leg") + self.NUM_ACTIONS

        self.horizontalHeader().setMinimumSectionSize(0)
        header_font = QFontMetrics(QFont(FONT, H3_FONT))
        contents_font = QFontMetrics(QFont(FONT, CONTENTS_FONT))
        max_shortname_width = max(
            max(
                contents_font.width(shortname)
                for shortname in table_data.keys()),
            header_font.width(columns[0]) + self.ICON_DIMENSION,
        )
        max_airport_width = max(
            max(contents_font.width(table_data[row][0]) for row in table_data),
            header_font.width(columns[1]) + self.ICON_DIMENSION,
        )
        max_leg_width = max(
            max(contents_font.width(table_data[row][1]) for row in table_data),
            header_font.width(columns[2]) + self.ICON_DIMENSION,
        )
        self.setColumnWidth(0 + self.NUM_ACTIONS,
                            max_shortname_width + self.CELL_PADDING)
        self.setColumnWidth(1 + self.NUM_ACTIONS,
                            max_airport_width + self.CELL_PADDING)
        self.setColumnWidth(2 + self.NUM_ACTIONS,
                            max_leg_width + self.CELL_PADDING)

        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setWordWrap(True)
        self.setMaximumHeight(20 + self.horizontalHeader().height() + sum(
            self.rowHeight(i) for i in range(self.rowCount())))

    def populateData(self, table_data, columns):
        for rowNum, shortname in enumerate(table_data):
            self.setItem(rowNum, 0 + self.NUM_ACTIONS,
                         QTableWidgetItem(shortname))
            self.item(rowNum, 0 + self.NUM_ACTIONS).setFlags(self.ITEM_FLAG)
            for colNum, val in enumerate(table_data[shortname]):
                item = QTableWidgetItem(val)
                if colNum == columns.index("Leg") - 1:
                    if val == file_constants.EUROPE_NAME:
                        icon = QIcon()
                        icon.addPixmap(
                            QPixmap(EUROPE_ICON).scaled(10, 10),
                            QIcon.Disabled)
                        item.setIcon(icon)
                        color = QColor()
                        color.setNamedColor(TERTIARY)
                        item.setForeground(color)
                    elif val == file_constants.FLYAWAY_NAME:
                        icon = QIcon()
                        icon.addPixmap(
                            QPixmap(FLYAWAY_ICON).scaled(10, 10),
                            QIcon.Disabled)
                        item.setIcon(icon)
                        color = QColor()
                        color.setNamedColor(SECONDARY)
                        item.setForeground(color)
                self.setItem(rowNum, colNum + 1 + self.NUM_ACTIONS, item)
                self.item(rowNum, colNum + 1 + self.NUM_ACTIONS).setFlags(
                    self.ITEM_FLAG)

    def changeHeaderItem(self, colIndex, icon, colName=None):
        if colName == None:
            colName = self.horizontalHeaderItem(colIndex).text()
        newItem = QTableWidgetItem(colName)
        if icon != None:
            newItem.setIcon(icon)
        newItem.setTextAlignment(Qt.AlignVCenter)
        self.setHorizontalHeaderItem(colIndex, newItem)

    @Slot(int, int)
    def tableClickAction(self, row, col):
        if col == 0:
            pass
            # REMEMBER TO MODIFY BOTH TABLE AND RACEEDIT.RACES
            # Must use setStringList
        elif col == 1:
            raceList = self.mainWindow.race_data.races
            raceList.remove(self.item(row, self.NUM_ACTIONS).text())
            self.removeRow(row)

    @Slot(int)
    def sortTable(self, colIndex):
        if colIndex in range(self.NUM_ACTIONS):
            return
        if (colIndex == self.sortedCol) and (self.order == Qt.AscendingOrder):
            self.order = Qt.DescendingOrder
            icon = self.DOWN_ARROW
        else:
            self.order = Qt.AscendingOrder
            icon = self.UP_ARROW

        self.sortItems(colIndex, self.order)
        self.changeHeaderItem(self.sortedCol, self.COMBINED_ARROW)
        self.changeHeaderItem(colIndex, icon)
        self.sortedCol = colIndex

    @Slot(int, int)
    def hoverAction(self, row, col):
        if col == 1:
            self.item(row, col).setIcon(self.RED_BIN)

    @Slot(int, int)
    def cellExitAction(self, row, col):
        if col == 1:
            self.item(row, col).setIcon(self.BLACK_BIN)

    @Slot(str)
    def filtered(self, text):
        legColIndex = 2 + self.NUM_ACTIONS
        if text == "All":
            showRow = lambda rowIndex: True
        else:
            showRow = lambda rowIndex: text == self.item(
                rowIndex, legColIndex).text()
        for rowIndex in range(self.rowCount()):
            self.setRowHidden(rowIndex, not showRow(rowIndex))

    @Slot(str)
    def searched(self, text):
        shortnameColIndex = self.NUM_ACTIONS
        shortnames = list(self.getData().keys())
        if text in shortnames:
            for rowIndex in range(self.rowCount()):
                self.setRowHidden(
                    rowIndex,
                    text != self.item(rowIndex, shortnameColIndex).text())
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No races with this shortname.",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )


##class MyComboBox(QComboBox):
##
##    def __init__(self, options):
##        super().__init__()
##        for option in options:
##            self.addItem(option)
##        self.setStyleSheet("""
##            QComboBox{{
##                border: 1px solid {secondary};
##                min-height: 32px;
##                max-height: 32px;
##                background-color: {secondary};
##                color: white;
##                width: 65px;
##                border-top-left-radius: {radius}px;
##                border-bottom-left-radius: {radius}px;
##            }}
##            QComboBox::drop-down{{
##                border: 0px;
##            }}
##            QComboBox::down-arrow{{
##                image: url("{COMBOBOX_ARROW}");
##                width: 40px;
##            }}
##        """.format(secondary=SECONDARY,
##                   radius="4",
##                   COMBOBOX_ARROW=COMBOBOX_ARROW))
##
##    @Slot()
##    def lineEditPressed(self):
##        self.showPopup()


class RacesPage(TablePage):

    def __init__(self, mainWindow):
        super().__init__(mainWindow)

        self.addPageHeaders("Race List", "Add, modify or delete races")
        self.mainLayout.addSpacing(15)

        self.addTableControls()
        self.mainLayout.addSpacing(15)

        self.addTable(mainWindow.race_data.table_data)
        self.mainLayout.addStretch(1)
        self.mainLayout.setStretchFactor(self.table, 1000)

    def addTableControls(self):
##        self.filter = MyComboBox(["All", "Europe", "Flyaway"])
##        filterLineEdit = FilterLineEdit()
##        self.filter.setLineEdit(filterLineEdit)
##        filterLineEdit.pressed.connect(self.filter.lineEditPressed)

        self.searchBar = RaceEdit(self.mainWindow.race_data.races, "Search by short name...")
        self.searchBar.setPlaceholderText("Search by short name...")
        self.searchBar.setStyleSheet("""
            QLineEdit{{
                height: 32px;
                color: {secondary};
                padding-left: 4px;
                border: 1px solid lightGray;
            }}
            QLineEdit:focus{{
                border: 2px solid {secondary};
            }}
        """.format(secondary=SECONDARY))

        self.searchButton = QPushButton()
        self.searchButton.setIcon(QIcon(SEARCH_ICON))
        self.searchButton.setStyleSheet("""
            QPushButton{{
                height: 34px;
                width: 33px;
                background-color: {secondary};
                border-top-right-radius: {radius}px;
                border-bottom-right-radius: {radius}px;
                border-right-style: dashed;
            }}
            QPushButton:hover{{
                background-color: {hover};
            }}
            QPushButton:pressed{{
                background-color: {pressed};
            }}
        """.format(secondary=SECONDARY, radius="4", pressed = PRESSED,
                   hover=HOVER))

        self.addRaceButton = QPushButton("Add Race")
        self.addRaceButton.setStyleSheet("""
            background-color: {secondary};
            color: white;
            height: 32px;
            width: 100px;
            border-radius: 4px;
        """.format(secondary=SECONDARY))

        self.tableControls = QHBoxLayout()
        self.tableControls.setSpacing(0)
        #self.tableControls.addWidget(self.filter)
        self.tableControls.addWidget(self.searchBar)
        self.tableControls.setStretchFactor(self.searchBar, 64)
        self.tableControls.addWidget(self.searchButton)
        self.tableControls.addStretch(32)
        self.tableControls.addWidget(self.addRaceButton)
        self.tableControls.addStretch(1)
        self.mainLayout.addLayout(self.tableControls)

    def addTable(self, table_data):
        columns = ["Airport", "Leg", "Address"]
        self.table = TableWidget(table_data, columns)
        self.mainLayout.addWidget(self.table)

        #self.filter.currentTextChanged.connect(self.table.filtered)
        self.searchButton.clicked.connect(self.tableSearched)

    @Slot()
    def tableSearched(self):
        search = self.searchBar.text()
        self.table.searched(search)


class RoutesPage(TablePage):

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        # Add widgets to main layout
        self.addPageHeaders("Routes",
                            "Set the intended route between any two races.")
        self.mainLayout.addStretch(1)


class IntervalsPage(ListPage):

    def __init__(self, INTERVALS_INFO, mainWindow):
        self.INTERVALS_INFO = INTERVALS_INFO

        super().__init__(mainWindow)
        # Add widgets to main layout
        self.addPageHeaders()
        self.addScrollable([], SPACING_LARGE)

    def addPageHeaders(self):
        super().addPageHeaders("Intervals")
        self.infoButton_img = convertImageColor(QImage(INFO_ICON), range(30),
                                                range(30), range(30),
                                                QColor("grey"))
        self.infoButton = QPushButton(QPixmap(self.infoButton_img), "")
        dimension = QFontMetrics(QFont(FONT, H2_FONT)).height() // 2
        self.infoButton.setStyleSheet(f"""
            background-color: white;
            border: none;
            width: {dimension}px;
            height: {dimension}px;
        """)
        self.infoButton.clicked.connect(self.openInfoDialog)
        self.pageHeaders.addWidget(self.infoButton)
        self.pageHeaders.addStretch()

        self.addSelect()
        self.mainLayout.addStretch(SPACING_SMALL)

    def addSelect(self):
        self.descriptionRow = QHBoxLayout()
        self.descriptionLabel = QLabel()
        self.descriptionLabel.setTextFormat(Qt.RichText)
        self.descriptionLabel.setText(
            "<p style='font-size:{size}px;' style='font-family:{font};'><b style='color:{secondary};'>Select</b> a race</p>"
            .format(secondary=SECONDARY, font={FONT}, size=CONTENTS_FONT))
        self.descriptionRow.addWidget(self.descriptionLabel)
        self.descriptionRow.addStretch()

        self.selectionRow = QHBoxLayout()
        self.selectionBox = RaceEdit(self.mainWindow.race_data.races, "Eg Australia")
        self.selectionRow.addWidget(self.selectionBox)
        self.selectionRow.addStretch()

        self.selectLayout = QVBoxLayout()
        self.selectLayout.addLayout(self.descriptionRow)
        self.selectLayout.addLayout(self.selectionRow)

        self.mainLayout.addLayout(self.selectLayout)

    @Slot()
    def openInfoDialog(self):
        dialogBox = QMessageBox()
        dialogBox.setText(self.INTERVALS_INFO)
        dialogBox.setWindowTitle("About intervals")
        dialogBox.setWindowIcon(QIcon(QPixmap(self.infoButton_img)))
        dialogBox.exec()
        
        
class CalendarPage(ListPage):

    def __init__(self, mainWindow, calendar):
        super().__init__(mainWindow)
        self.calendar = calendar
        
        self.addPageHeaders("Final Calendar")
        self.mainLayout.addSpacing(SPACING_MEDIUM)

        topControls = QVBoxLayout()
        self.totalCO2 = QLabel("")
        self.totalCO2.setTextFormat(Qt.RichText)

        self.calendarLayout = QVBoxLayout()
        self.calendarItems = []
        self.addScrollable([], SPACING_LARGE)

        self.drawCalendarInfo()

    def drawCalendarInfo(self):
        self.totalCO2.setText(
            "<p style='font-size:{size}px;' style='font-family:{font};' style='color:gray;'>Total emitted: <b style='color:{secondary};'>{emitted} tonnes CO2</b></p>"
        .format(secondary=SECONDARY, font={FONT}, size=CONTENTS_FONT, emitted = self.calendar[0]))
        for calendarItem in self.calendarItems:
            self.calendarLayout.removeItem(calendarItem)
        for raceIndex, race in enumerate(self.calendar[1]):
            newRow = self.createCalendarItem(raceIndex + 1, race)
            newRow = QHBoxLayout()
            newRow.addWidget(QLabel("hi"))
            self.calendarLayout.addLayout(newRow)
            self.calendarLayout.addSpacing(SPACING_SMALL)
        self.calendarLayout.addStretch()

    def createCalendarItem(self, raceNum, race):
        layout = QHBoxLayout()
        numberLabel = QLabel(f"{raceNum}.")
        numberLabel.setFont(QFont(FONT, CONTENTS_FONT))
        nameLabel = QLabel(f"{race}")
        nameLabel.setFont(QFont(FONT, CONTENTS_FONT))
        layout.addWidget(numberLabel)
        layout.addStretch(1)
        layout.addWidget(nameLabel)
        layout.addWidget(QLabel("Hi"))
        layout.addStretch(15)
        return layout


class RaceData:
    def __init__(self, dict_):
        self.dict_ = dict_
        self.races = sorted(list(dict_.keys()))
        self.table_data = file_formatting.get_table_data(dict_, [file_constants.TWS_INDEX])

    def __len__(self):
        return len(self.dict_)


class MainWindow(QMainWindow):

    def __init__(self, race_data, routes, intervals_info, calendar):
        super().__init__()
        self.race_data = RaceData(race_data)
        self.routes = routes
        
        self.setWindowTitle("Green Calendar F1")
        self.setGeometry(WINDOW_POS[0], WINDOW_POS[1], WINDOW_SIZE[0], WINDOW_SIZE[1])        
        self.setWindowIcon(QIcon(APP_ICON))
        self.displayInit(intervals_info, calendar)

    def displayInit(self, intervals_info, calendar):
        self.displayToolBar()
        self.displayTitleLabel()

        self.pages = QStackedWidget()
        self.racesPage = RacesPage(self)
        self.pages.addWidget(self.racesPage)
        self.routesPage = RoutesPage(self)
        self.pages.addWidget(self.routesPage)
        self.intervalsPage = IntervalsPage(intervals_info, self)
        self.pages.addWidget(self.intervalsPage)
        self.calendarPage = CalendarPage(self, calendar)
        self.pages.addWidget(self.calendarPage)
        self.pages.setCurrentIndex(0)

        self.centralWidget = QWidget()
        self.topLayout = QVBoxLayout(self.centralWidget)
        self.topLayout.addWidget(self.titleLabel)
        self.topLayout.addWidget(self.pages)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setSpacing(0)
        self.setCentralWidget(self.centralWidget)

        self.setMinimumHeight(
            self.calendarButton.mapToGlobal(
                QPoint(0, self.calendarButton.height())).y()
        )  # TODO: change this to be general last button of toolbar
        self.setStyleSheet("""
            QMainWindow{
                background-color: white;
            }
        """)
        self.show()

    def displayTitleLabel(self):
        self.titleLabel = QLabel()
        self.titleLabel.setPixmap(
            QPixmap(APP_ICON).scaled(20, TOP_MARGIN - 2 * TITLE_PADDING - SINK,
                                     Qt.KeepAspectRatioByExpanding))
        self.titleLabel.setAlignment(Qt.AlignHCenter)
        self.titleLabel.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.titleLabel.setStyleSheet("""
            background-color: {secondary};
            border-bottom-color: {darkSecondary};
            border-bottom-style: solid;
            border-bottom-width: {SINK}px;
            padding-bottom: {TITLE_PADDING}px;
            padding-top: {TITLE_PADDING}px;
        """.format(
            secondary=SECONDARY,
            darkSecondary=DARK_SECONDARY,
            SINK=SINK,
            TITLE_PADDING=TITLE_PADDING,
        ))

    def displayToolBar(self):
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet("""
            QToolBar{{
                background-color: {secondary};
                border: none;
            }}
            QToolBar:separator{{
                background-color: {secondary};
                height: 1px;
            }}
        """.format(secondary=SECONDARY))
        self.toolbarButtonGroup = QButtonGroup(self)
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBarButton("Races",
                              RACES_ICON,
                              topButton=True,
                              separators=TOP_MARGIN - 3)
        self.addToolBarButton("Routes", ROUTES_ICON)
        self.addToolBarButton("Intervals", INTERVALS_ICON)
        self.calendarButton = self.addToolBarButton("Calendar",
                                                    CALENDAR_ICON,
                                                    separators=int(TOP_MARGIN /
                                                                   PHI))
        self.toolbarButtonGroup.buttonPressed.connect(self.changePage)

        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.toolbar.setAllowedAreas(Qt.LeftToolBarArea)

    def addToolBarButton(self,
                         buttonText,
                         imageFile,
                         separators=0,
                         topButton=False):
        button = MyToolButton()
        button.setIcon(QIcon(imageFile))
        button.setFont(QFont(FONT, 10))
        button.setText(buttonText)
        button.setCheckable(True)
        if topButton:
            button.setChecked(topButton)
            button.setStyleSheet("""
                border-top-color: {secondary};
                border-top-style: solid;
                border-top-width: {SINK}px;
                height: {TOP_BUTTON_HEIGHT}px;
            """.format(secondary=SECONDARY,
                       SINK=SINK,
                       TOP_BUTTON_HEIGHT=SINK + 30))
        for i in range(separators):
            self.toolbar.addSeparator()
        self.toolbar.addWidget(button)
        self.toolbarButtonGroup.addButton(
            button, len(self.toolbarButtonGroup.buttons()))
        return button

    def changePage(self, button):
        self.pages.setCurrentIndex(self.toolbarButtonGroup.id(button))

    def closeEvent(self, event):
        global race_data, routes
        race_data = self.race_data.dict_
        routes = self.routes
        QMainWindow.closeEvent(self, event)


if __name__ == "__main__":
    with open(file_constants.INTERVALS_INFO_PATH) as intervals_info_file:
        intervals_info = intervals_info_file.read()
    with open(file_constants.RACE_DATA_PATH) as data_file:
        race_data = json.load(data_file)
    with open(file_constants.ROUTES_PATH) as routes_file:
        routes = json.load(routes_file)
    with open(file_constants.CALENDAR_PATH) as calendar_file:
        calendar = json.load(calendar_file)
    
    app = QApplication([])
    app.setStyleSheet(STYLE_SHEET)
    window = MainWindow(race_data, routes, intervals_info, calendar)
    exit_code = app.exec_()
    with open(file_constants.RACE_DATA_PATH, "w") as data_file:
        json.dump(race_data, data_file)
    with open(file_constants.ROUTES_PATH, "w") as routes_file:
        json.dump(routes, routes_file)
    sys.exit(exit_code)
