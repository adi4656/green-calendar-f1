# Two dropdowns allow selection of race. (Selection of same race allowed - won't affect final result)
# Series of numerical fields. Each one has: dist, tonnage, efficiency
# Total dist at bottom w calculate and reset buttons

from tkinter import *
import json, math


def calculate_total():
    global infoend
    total = 0
    for rowindex, row in enumerate(entries):
        tonnage = row[0].get()
        dist = row[1].get()
        efficiency = row[2].get()
        if ((tonnage.upper() == "IMPOSSIBLE") or (dist.upper() == "IMPOSSIBLE")
                or (efficiency.upper() == "IMPOSSIBLE")):
            total = math.inf
            break
        elif (not tonnage) or (not dist) or (not efficiency):
            pass
        elif not tonnage.replace(".", "", 1).isdigit():
            infoend["text"] = "Row " + str(rowindex +
                                           1) + ", column 1 is invalid."
            return
        elif not dist.replace(".", "", 1).isdigit():
            infoend["text"] = "Row " + str(rowindex +
                                           1) + ", column 2 is invalid."
            return
        elif not efficiency.replace(".", "", 1).isdigit():
            infoend["text"] = "Row " + str(rowindex +
                                           1) + ", column 3 is invalid."
            return
        else:
            cost = float(tonnage) * float(dist) * float(efficiency)
            total += cost
    infoend["text"] = "Total CO2 emissions: " + str(total)
    return total


def reset():
    global infoend, entries
    infoend["text"] = "Total CO2 emissions: 0"
    for row in entries:
        for field in row:
            field.delete(0, END)
            field.insert(0, "0")


def save():
    global adjacencies
    total = calculate_total()
    if total == None:
        return
    if (race1_var.get() == "") or (race2_var.get() == ""):
        infoend[
            "text"] = "Select a source and destination race from dropdowns at top."
        return
    adjacencies[(race1_var.get(), race2_var.get())] = total


def create_row():
    newrow = []
    for j in range(3):
        newentry = Entry(root)
        newentry.insert(0, "0")
        newentry["width"] = DROPDOWN_WIDTH
        newrow.append(newentry)
    return newrow


def add_row():
    global entries
    # Wipe screen from first entry down
    for row in entries:
        for entity in row:
            entity.grid_forget()
    # Add new entry into the list
    entries.append(create_row())
    # Redraw
    draw()


def draw():
    # Draw in entry rows
    for row_index, row in enumerate(entries):
        for field_index, field in enumerate(row):
            field.grid(row=row_index + 3, column=field_index)
    # Draw in bottom widgets
    plusbtn.grid(row=len(entries) + 3, column=1, pady=(0, ENTRYHEIGHT / 2))
    infoend.grid(row=len(entries) + 4, column=1, rowspan=2)
    calculatebtn.grid(row=len(entries) + 6, column=1, pady=(ENTRYHEIGHT, 0))
    resetbtn.grid(row=len(entries) + 7, column=1)
    savebtn.grid(row=len(entries) + 8, column=1)
    # Size window according to number of entry rows
    initial_height = int(INIT_DIMENSIONS.split("x")[1])
    extra_rows = len(entries) - 1
    new_height = initial_height + extra_rows * ENTRYHEIGHT
    initial_width = int(INIT_DIMENSIONS.split("x")[0])
    root.geometry(str(initial_width) + "x" + str(new_height))


# Load data
with open("races.txt", "r") as infile:
    data = json.load(infile)
    all_races = data["Europe"] + data["World Races"] + ["Summer break"]
with open("adjacencymatrix.txt", "r") as infile:
    adjacencies = json.load(infile)
# Initialise window
ENTRYHEIGHT = 20
initial_num_entries = 1
INIT_DIMENSIONS = "1450x250"
DROPDOWN_WIDTH = 75
root = Tk()
root.title("Distance controller")
root.geometry(INIT_DIMENSIONS)
root.resizable(False, False)
app = Frame(root)
app.grid()
# Layout widgets
# Two dropdowns
dropdown1_description = Label(root, text="Origin Race")
dropdown1_description.grid(row=0, column=0)
dropdown2_description = Label(root, text="Destination Race")
dropdown2_description.grid(row=0, column=1)
race1_var = StringVar(root)
race2_var = StringVar(root)
dropdown1 = OptionMenu(root, race1_var, *all_races)
dropdown1["width"] = DROPDOWN_WIDTH
dropdown1.grid(row=1, column=0)
dropdown2 = OptionMenu(root, race2_var, *all_races)
dropdown2["width"] = DROPDOWN_WIDTH
dropdown2.grid(row=1, column=1)
# Header columns for entry
info1 = Label(root, text="Tonnage transported on leg")
info2 = Label(root, text="Distance of leg / km")
info3 = Label(root, text="CO2 / ton / km")
info1.grid(row=2, column=0)
info2.grid(row=2, column=1)
info3.grid(row=2, column=2)
# initial_num_entries entries
entries = []
for i in range(0, initial_num_entries):
    newrow = create_row()
    entries.append(newrow)
# Total distance / error message and buttons
plusbtn = Button(root, text="+", command=add_row)
infoend = Label(root, text="Total CO2 emissions: 0")
calculatebtn = Button(root, text="Calculate", command=calculate_total)
resetbtn = Button(root, text="Reset", command=reset)
savebtn = Button(root, text="Save", command=save)
draw()

root.mainloop()

with open("adjacencymatrix.txt", "w") as outfile:
    json.dump(adjacencies)
