
# README
## About
This software accepts from the user a set of locations where Formula One races will take place in a season. It then calculates an ordered list of all these races, representing the order they should take place in during the season. This order is such that the total CO2 equivalent emitted by transporting equipment from each race to the next is minimised across all possible orderings.  
The project is intended to have a GUI to input locations and other constraints and to view the order, plus a backend that calculates the order and makes some API calls. Unfortunately the GUI code is too complex right now and so is undergoing a refactor; it is not complete. **However the backend is fully functional and tested.**
## Important
**Please do not make modifications to the list of race locations.** (`data/race_locations.txt`). This will result in calls to two web APIs that I will be billed for. The calls for the existing data have been cached and there should be no problems running this.  
**Please do not share this code with too many people.** Firstly since there are paid API keys in the .env file, and secondly since I am talking to F1 officials about delivering this software to them.
## Setup
As of now, setup has been tested on Windows 10 and 11 only. Other prerequisites are Python 3.7.8 or above and pip.  
To set up, clone the repo, then run the following commands (making sure `python` refers to Python 3.7.8 or above):
`cd green-calendar-f1`  
`python -m venv green-calendar-f1-env`   
`green-calendar-f1-env\Scripts\activate.bat`    
`pip install -r requirements.txt`    
This will set up a virtual environment `green-calendar-f1-env` with the required dependencies. It may then be used in the standard fashion of Python virtual environments.

## Folder-by-folder
**src**: There are 3 files here. `scheduler.py` contains the logic for calculating the best order; `distance_calculator.py` handles web API calls to calculate the real-world carbon emissions of journeys; and `main.py` will be the GUI program with which the user interacts. Since it is currently not complete, **outputting the order is handled through the command line by `scheduler.py`**.  
**tests**: Tests for the scheduling, as real-world distance calculation is difficult to test programatically. The tests test both the accuracy of the scheduler and the running time, comparing the latter's growth to the theoretically expected growth.  
**data**: Contains various text files storing data about the races. Due to the GUI code being broken, this is currently the point of entry for the project.  
**dev**: Contains three old files that will soon be deleted, and also `resource_generator.py`. When run, this produces `resources.py`  in the `images` directory.  
**images**: Images to be used for the GUI. The GUI does not access the images directly but via `resources.py`, which encodes the images.

## Notes on scheduler algorithm
The scheduler algorithm is heavily based off the Held-Karp algorithm. There are three significant differences:  
 1. The problem at hand more closely resembles a TSP with Time Windows than a classic TSP. The scheduler program must check to ensure races in the calculated order fall within one of their time windows.  
 2. Classic TSP asks for a Hamiltonian cycle; the scheduler program looks for an ayclic Hamiltonian path (I am still waiting to hear back on how equipment is shipped back at the end of the season). However the algorithm is easily adapted for this.  
 3. Classic Held-Karp starts with the smallest possible subsets and iteratively builds up to the set of races/cities itself. This algorithm starts with the set of races/cities itself and recursively goes down to the smallest possible subsets. There is no reason for this other than it made the code somewhat more readable.
