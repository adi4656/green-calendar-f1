from tkinter import *
import json


def create_row(value1="", value2=""):
    field1 = Entry(root, justify=RIGHT)
    field1.insert(0, str(value1))
    field1["width"] = DROPDOWN_WIDTH
    field2 = Entry(root, justify=RIGHT)
    field2.insert(0, str(value2))
    field2["width"] = DROPDOWN_WIDTH
    return [field1, field2]


def wipe():
    # Wipe screen from first entry down
    for row in entries:
        for entity in row:
            entity.grid_forget()


def draw():
    wipe()
    # Draw in entry rows
    for row_index, row in enumerate(entries):
        for field_index, field in enumerate(row):
            field.grid(row=row_index + 3, column=field_index)
    # Draw in bottom widgets
    plusbtn.grid(row=len(entries) + 3,
                 column=0,
                 columnspan=2,
                 pady=(0, ENTRYHEIGHT))
    infoend.grid(row=len(entries) + 4, column=0, columnspan=2)
    if restorebtn_exists:
        restorebtn.grid(row=len(entries) + 5, column=0, columnspan=2)
    savebtn.grid(row=len(entries) + 6, column=0, columnspan=2)
    # Size window according to number of entry rows
    initial_height = int(INIT_DIMENSIONS.split("x")[1])
    extra_rows = len(entries) - 1
    new_height = initial_height + extra_rows * ENTRYHEIGHT
    initial_width = int(INIT_DIMENSIONS.split("x")[0])
    root.geometry(str(initial_width) + "x" + str(new_height))


def add_row():
    global entries
    wipe()
    # Add new entry into the list
    entries.append(create_row())
    # Redraw
    draw()


def validate(start, end, row_index):
    """Returns False if time window (start,end) is valid...
    ...otherwise returns an appropriate error message"""
    if start == "":
        return "Please enter a value for row " + str(row_index +
                                                     1) + ", start field."
    if end == "":
        return "Please enter a value for row " + str(row_index +
                                                     1) + ", end field."
    if (not start.isdecimal()) and (not ((len(start) >= 2) and
                                         (start[0] == "-") and
                                         (start[1:].isnumeric()))):
        return (
            "Start field, row " + str(row_index + 1) +
            " contains unaccepted characters or characters in the wrong place; please only enter integers."
        )
    if (not end.isdecimal()) and (not ((len(end) >= 2) and (end[0] == "-") and
                                       (end[1:].isnumeric()))):
        return (
            "End field, row " + str(row_index + 1) +
            " contains unaccepted characters or characters in the wrong place; please only enter integers."
        )
    start = int(start)
    end = int(end)
    if start == 0:
        return "Start field, row " + str(row_index + 1) + " is zero."
    if end == 0:
        return "End field, row " + str(row_index + 1) + " is zero."
    start_positivised = start
    end_positivised = end
    if start < 0:
        start_positivised = len(ALL_RACES) + start
    if end < 0:
        end_positivised = len(ALL_RACES) + end
    if (start_positivised < 0) or (start_positivised > len(ALL_RACES)):
        return "Start field, row " + str(row_index + 1) + " is out of range."
    if (end_positivised < 0) or (end_positivised > len(ALL_RACES)):
        return "End field, row " + str(row_index + 1) + " is out of range."
    if start_positivised > end_positivised:
        return ("Row " + str(row_index + 1) +
                " has a start position after the end position.")
    return False


def save():
    global timewindows
    race = race_var.get()
    if race == "":  # i.e. no race selected
        infoend["text"] = "Please select a race."
        return
    race_windows = []
    for row_index, entry in enumerate(entries):
        start = entry[0].get()
        end = entry[1].get()
        validation = validate(start, end, row_index)
        if validation == False:
            race_windows.append([start, end])
        else:
            infoend["text"] = validation
            return
    timewindows[race] = race_windows


def load(throwaway=""):
    global entries
    if infoend["text"] != DEFAULT_INFO:
        # User has been warned to select a race. Don't wipe and rewrite
        infoend["text"] = DEFAULT_INFO
    else:
        wipe()
        race = race_var.get()
        if race not in timewindows:
            race_windows = [[1, -1]]
        else:
            race_windows = timewindows[race]
        entries = []
        for window in race_windows:
            entries.append(create_row(window[0], window[1]))
        draw()


# Load data
with open("timewindows.txt", "r") as infile:
    timewindows = json.load(infile)
with open("races.txt", "r") as infile:
    ALL_RACES = json.load(infile)
# Initialise window
ENTRYHEIGHT = 20
initial_num_entries = 1
INIT_DIMENSIONS = "1000x235"
DROPDOWN_WIDTH = 75
DEFAULT_INFO = "Enter 1 to " + str(
    len(ALL_RACES)) + " or the negative equivalent."
root = Tk()
root.title("Time Window controller")
root.geometry(INIT_DIMENSIONS)
root.resizable(False, False)
app = Frame(root)
app.grid()
# Lay out widgets
# Dropdown for selecting race
dropdown_description = Label(root, text="SELECT RACE:")
dropdown_description.grid(row=0, column=0)
race_var = StringVar(root)
dropdown = OptionMenu(root, race_var, *ALL_RACES, command=load)
dropdown["width"] = DROPDOWN_WIDTH
dropdown.grid(row=1, column=0, pady=(0, ENTRYHEIGHT))
# Header columns for entry
info1 = Label(root, text="Earliest Possible Position in Season")
info2 = Label(root, text="Latest Possible Position in Season")
info1.grid(row=2, column=0)
info2.grid(row=2, column=1)
# Entries, buttons, info
entries = []
for i in range(initial_num_entries):
    newrow = create_row()
    entries.append(newrow)
plusbtn = Button(root, text="+", command=add_row)
infoend = Label(root, text=DEFAULT_INFO)
savebtn = Button(root, text="Save race's new windows", command=save)
restorebtn_exists = False
restorebtn = Button(root, text="Restore race's saved windows", command=load)
restorebtn_exists = True
draw()

root.mainloop()

with open("timewindows.txt", "w") as outfile:
    json.dump(timewindows, outfile)
