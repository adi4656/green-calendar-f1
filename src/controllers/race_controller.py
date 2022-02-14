import json, distance_calculator
from tkinter import *
from googlemaps import Client

gmaps = Client(key="AIzaSyDhM7uKfMIU7G6w2VN6q-UlCKAzwbn3jeE")

# Dict["Europe"] = race1, race2...
# Dict["World Races"] = race1, race2...
# Dict["Airports"] = race1, race2...


def valid_iata(iata):
    # Returns Boolean value representing whether iata stores valid IATA code
    if iata == "":
        return False
    iata = iata.upper()
    lines = []
    file = open("iata-name data.txt")
    lines = file.readlines()
    file.close()
    found = False
    for line in lines:
        line = line.strip().split(",")[1:]

        if '"' + iata + '"' in line:
            found = True
            break
    return found


def remove_race():
    # Removes the race currently selected on the drop-down.
    global all_races, dropdown_var
    try:
        loc = all_races[state].index(dropdown_var.get())
        if state == 1:  # must offset world race index by number of european races
            loc += len(all_races[0])
        all_races[state].remove(dropdown_var.get())
    except ValueError:
        return
    else:
        # Delete race from all_races
        if (state == 1) or (state == 0):
            del all_races[2][loc]
    dropdown["menu"].delete(0, "end")  # deletes all races from dropdown
    for string in all_races[state]:  # loop through all remaining races...
        dropdown["menu"].add_command(
            label=string, command=lambda value=string: dropdown_var.set(
                value))  # ...and add them back to dropdown
    if len(all_races[state]) != 0:
        dropdown_var.set(all_races[state][-1])
    else:
        dropdown_var.set("")


def add():
    # Adds the race (with validation) currently entered OR adds the airport if that is pending
    global all_races, entry, dropdown, enter_btn, race_temp, warning
    if enter_btn["text"] == "Enter IATA code":
        string = entry.get()
        if not valid_iata(string):
            warning["text"] = "Invalid IATA code"

            return
        entry.delete(0, "end")
        if state == 0:
            all_races[2].insert(len(all_races[0]), string)
            all_races[0].append(race_temp)
        if state == 1:
            all_races[1].append(race_temp)
            all_races[2].append(string)
        dropdown["menu"].add_command(
            label=race_temp,
            command=lambda value=race_temp: dropdown_var.set(value))
        dropdown_var.set(all_races[state][-1])
        race_temp = None
        warning["text"] = ""
        enter_btn["text"] = "Enter race"

    else:
        warning["text"] = ""
        string = entry.get()
        if not valid(string):
            warning["text"] = "Invalid street address"

            return
        entry.delete(0, "end")
        if (state == 1) or (state == 0):
            enter_btn["text"] = "Enter IATA code"
            warning[
                "text"] = "Please enter corresponding airport IATA code for the race you just added."
            race_temp = string

            return


def toggle():
    # Toggle between Europe and World
    global state, dropwdown, toggle_btn, enter_btn, warning, race_temp, dropdown_var, entry
    state = int(not state)
    dropdown["menu"].delete(0, "end")
    for string in all_races[state]:
        dropdown["menu"].add_command(
            label=string, command=lambda value=string: dropdown_var.set(value))
    if len(all_races[state]) != 0:
        dropdown_var.set(all_races[state][0])
    else:
        dropdown_var.set("")
    toggle_btn["text"] = "Switch to " + ["World", "Europe"][state]
    enter_btn["text"] = "Enter race"
    warning["text"] = ""
    race_temp = None
    entry.delete(0, "end")
    pass


def valid(streetaddress):
    if streetaddress == "":
        return False
    return True


# Load data
with open("races.txt", "r") as infile:
    data = json.load(infile)
    all_races = [data["Europe"], data["World Races"], data["Airports"]]

# Initialise window
DROPDOWN_WIDTH = 75
DIMENSIONS = "1045x100"
state = 0  # 0 = Europe, 1 = World
race_temp = None  # Holds entered race while airport is being entered
root = Tk()
root.title("Race controller")
root.geometry(DIMENSIONS)
root.resizable(False, False)
app = Frame(root)
app.grid()
# Place widgets
dropdown_var = StringVar(root)
if len(all_races[state]) == 0:
    # In case no races, need some list for dropdown menu to be initialised
    all_races[state] = [""]
    all_races[1 - state] = [""]
dropdown_var.set(all_races[state][0])
dropdown = OptionMenu(root, dropdown_var, *all_races[state])
dropdown["width"] = DROPDOWN_WIDTH
dropdown.grid(row=0, column=0)
remove_btn = Button(root, text="Remove selected race", command=remove_race)
remove_btn.grid(row=1, column=0)
entry = Entry(root)
entry["width"] = DROPDOWN_WIDTH
entry.grid(row=0, column=2)
enter_btn = Button(root, text="Enter race", command=add)
enter_btn.grid(row=1, column=2)
toggle_btn = Button(root, text="Switch to World", command=toggle)
toggle_btn.grid(row=2, column=1)
warning = Label(root, text="")
warning.grid(row=2, column=2)
root.mainloop()
# Update new data to files
while "" in all_races[0]:
    all_races[0].remove("")
while "" in all_races[1]:
    all_races[1].remove("")
while "" in all_races[2]:
    all_races[2].remove("")
data = {
    "Europe": all_races[0],
    "World Races": all_races[1],
    "Airports": all_races[2]
}
with open("races.txt", "w") as outfile:
    json.dump(data, outfile)

# Update adjacency matrix by calling distance_calculator
# distance_calculator.main()
