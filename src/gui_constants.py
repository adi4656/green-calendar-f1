from math import sqrt


# FILENAMES
APP_ICON = ":/gold_star.png"
RACES_ICON = ":/races_icon.png"
ROUTES_ICON = ":/directions_icon.PNG"
INTERVALS_ICON = ":/intervals_icon.PNG"
CALENDAR_ICON = ":/gold_star.png"
COMBOBOX_ARROW = ":/combobox_arrow.PNG"
EUROPE_ICON = ":/europe_icon.png"
SEARCH_ICON = ":/search_icon.png"
FLYAWAY_ICON = ":/flyaway_icon.png"
UP_SORT_ICON = ":/combobox_arrow.PNG"
DOWN_SORT_ICON = ":/directions_icon.PNG"
PENCIL_ICON = ":/pencil.png"
BIN_ICON = ":/delete.png"
INFO_ICON = ":/info.png"

# MATHEMATICAL CONSTANTS
PHI = 0.5 * (1 + sqrt(5))

# STYLING
# Colours
_make_rgb = lambda components : "#" + "".join(components)
_secondary_components = ("30", "6e", "4c")
SECONDARY = _make_rgb(_secondary_components)
DARK_SECONDARY = SECONDARY
_pressed_components = ("43", "b6", "55")
PRESSED = _make_rgb(_pressed_components)
_hex_average = lambda x, y : hex(int((int(x, 16) + int(y, 16)) / 2))[2:]
_hover_components = (_hex_average(_secondary_components[i], _pressed_components[i]) for i in range(3))
HOVER = _make_rgb(_hover_components)
SECONDARY_TINT = "#dcefe5"
TERTIARY = "#2d7eff"
# Positioning
TOP_MARGIN = 55
SINK = 2
TITLE_PADDING = 5
SPACING_SMALL = 5
SPACING_MEDIUM = round(SPACING_SMALL * PHI)
SPACING_LARGE = round(SPACING_MEDIUM * PHI)
PAGE_SIDES_PADDING = round(SPACING_LARGE * PHI)
PAGE_TOP_PADDING = SPACING_LARGE
WINDOW_POS = (100, 100)
WINDOW_SIZE = (750 * PHI, 750)
# Fonts
FONT = "Arial"
SMALLEST_FONT = 11
CONTENTS_FONT = 14
H3_FONT = 16
H2_FONT = 18
H1_FONT = 21

STYLE_SHEET = """
        MyToolButton{{
            text-align: left;
            color: white;
            background-color: {secondary};
            border: none;
            width: 200px;
            height: 30px;
        }}
        MyToolButton:checked{{
            background-color: {pressed};
            font: bold;
            border-color: {secondary};
            border-style: solid;
            border-width: 1px;
            border-radius: 2px;
        }}
        MyToolButton:hover:!checked{{
            background-color: {hover};
        }}
        QHeaderView::section{{
            background-color: white;
            border: none;
            border-top-width: 1px;
            border-top-style: solid;
            border-top-color: lightGray;
            border-bottom-width: 2px;
            border-bottom-style: solid;
            border-bottom-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 gray, stop: 1 white);
            color: {secondary};
            font: bold;
            font-family: {font};
            font-size: {tableHeaderFontSize}px;
            padding-left: 2px;
            padding-top: 5px;
        }}
        QTableWidget{{
            font-family: {font};
            font-size: {tableFontSize}px;
            padding-left: 0px;
            border: none;
            border-right: 1px solid lightGray;
            color: black;
        }}
        QTableWidget::item{{
            border-bottom: 1px solid #C8C8C8;
        }}
""".format(
    secondary=SECONDARY,
    hover=HOVER,
    pressed=PRESSED,
    font=FONT,
    tableFontSize=CONTENTS_FONT,
    tableHeaderFontSize=H3_FONT,
)
