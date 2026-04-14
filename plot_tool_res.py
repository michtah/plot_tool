#
# IMPORTS
# The external packages that plot_tool uses. All of these come with a default python installation.
#

import tkinter as tk
from turtle import TurtleScreen, RawTurtle
import math as m

# ---------------------------------------------------------------- #
# DEFINITIONS                                                      #
# Defines variables that the program uses throughout its existence #
# ---------------------------------------------------------------- #

# the boundaries of the graph.
# llx and lly specify the x-y coordinates of the lower left corner
# urx and ury specify the x-y coordinates of the upper right corner
# this format matches with the world coordinate variables of the turtle package.
graphBounds = {
    "llx" : -2,
    "lly" : -2,
    "urx" :  2,
    "ury" :  2
}

# the resolution of the graphs (how far the graph plotter moves for each step)
graphResolution = 0.001

# defines the existing plots, which are stored as dictionaries.
# plot dict format:
#   - TYPE: defines the type of plot: FUNCTIONx, POINT, LINE, or POLYGON
#   - DATA: contains the actual data of the plot. Functions are stored as lambdas, Points as tuples, Polygons and Lines as lists of tuples.
#   - DISP: contains the string displayed as the data of the plot.
#   - COLR: contains the colour of the plot.
#   - SIZE: contains the thickness of the plotting brush.
#   - VISB: specifies if the current plot is visible.
plots = []

# defines the safe dictionary of words the user is allowed to use
# this is usual function in the math library, and some from the built in functions
safe_dict = {name: getattr(m, name) for name in dir(m) if not name.startswith('_')}
safe_dict["abs"] = abs
safe_dict["pow"] = pow
safe_dict["sum"] = sum
safe_dict["round"] = round
safe_dict["int"] = int
safe_dict["range"] = range

# ---------------------------------- #
# GRAPHICS                           #
# Defines the graphics for the plot. #
# ---------------------------------- #

# Create window and set size.
window = tk.Tk()
window.geometry("1500x1000")

# Create the canvas and the screen.
# The canvas is the physical placement of the screen
# which is where the turtle actually draws graphics
graphCanvas = tk.Canvas(width=1000, height=1000) # create canvas
graphCanvas.grid(row=0,column=0,rowspan=4)       # place canvas
graphScreen = TurtleScreen(graphCanvas)          # create screen
graphScreen.tracer(0, 0)                         # manual updates only
graphScreen.setworldcoordinates(graphBounds["llx"], graphBounds["lly"], graphBounds["urx"], graphBounds["ury"]) #set bounds to the graph bounds.

graphTurtle = RawTurtle(graphScreen, visible=False) # create invisible turtle.

# Configure grid rows to minimize spacing
window.grid_rowconfigure(0, weight=0)
window.grid_rowconfigure(1, weight=0)
window.grid_rowconfigure(2, weight=1)
window.grid_rowconfigure(3, weight=0)
window.grid_columnconfigure(1, weight=1)

# command entry location
commandEntry = tk.Entry(window, justify="left")
commandEntry.grid(row=0,column=1, padx=1, pady=0, sticky="ew")

# errors
errorString = tk.StringVar(window, value="") # create string variable to store plot information
errorLabel = tk.Label(window, textvariable=errorString, font=("Courier New", 9), wraplength=350, justify="left", height=1, fg="red", anchor="w") # create label that displays the plot information
errorLabel.grid(row=1, column=1, padx=2, pady=1, sticky="ew") # place this label

# plot list
plotsString = tk.StringVar(window, value="Plots:")
plotsLabel = tk.Label(window, textvariable=plotsString, font=("Courier New", 9), wraplength=350, justify="left", height=1, anchor="nw")
plotsLabel.grid(row=2,column=1, padx=2, pady=1, sticky="nsew")

# general graph info
infoString = tk.StringVar(window, value="Graph Info:") # create string variable to store plot information
infoLabel = tk.Label(window, textvariable=infoString, font=("Courier New", 9, "italic"), wraplength=350, justify="left", height=1, anchor="w") # create label that displays the plot information
infoLabel.grid(row=3,column=1, padx=2, pady=5, sticky="ew") # place this label

# ------------------------------------ #
# DEFINITION AND GUI HELPERS           #
# Functions to get and set definitions #
# Functions to modify the GUI          #
# ------------------------------------ #

# returns the graph's dimensions (x,y) as a tuple.
def getGraphDimensions():
    global graphBounds
    return (graphBounds["urx"] - graphBounds["llx"], graphBounds["ury"] - graphBounds["lly"])

# returns the centre of the graph as a tuple.
def getGraphCentre():
    global graphBounds
    return (graphBounds["urx"]*0.5 + graphBounds["llx"]*0.5, graphBounds["ury"]*0.5 + graphBounds["lly"]*0.5)

# Updates the screen's world coordinates using graphBounds
def updateBounds():
    graphScreen.setworldcoordinates(graphBounds["llx"], graphBounds["lly"], graphBounds["urx"], graphBounds["ury"])

# changes the display of the errors label
def displayError(error):
    errorString.set(error)

# changes the display of the graph info
def displayInfo():
    global plots
    width, height = getGraphDimensions()
    centre_x, centre_y = getGraphCentre()
    numberOfPlots = len(plots)

    infoString.set("Size  : " + formatNumber(width) + chr(ord("×")) + formatNumber(height) + " | Centre: " + formatNumber(centre_x) + ", " + formatNumber(centre_y) + " | Plots : " + str(numberOfPlots))

# changes the display of the plot info
def displayPlots():
    displayStr = "Plots:"
    for id, plot in enumerate(plots):
        displayStr += "\nID: {:02d}".format(id) + " | [" + ("X" if plot["VISB"] else " ") + "] | " + plot["DISP"]
    plotsString.set(displayStr)


# ---------------------------------------------------------- #
# HELPERS                                                    #
# Helper functions that aren't commands the user can access. #
# ---------------------------------------------------------- #

# takes a string and deduces its plot type:
#   - FUNCTION1 : the type "f(t) = t**2" etc.
#   - FUNCTION2 : the type "y = x**2" etc.
#   - FUNCTION3 : the type "x**2" etc.
#   - POINT     : the type "(a,b)" etc.
#   - LINE      : the type "[(a,b),(c,d) ... (y,z)]" etc.
#   - POLYGON   : the type "P[(a,b),(c,d) ... (y,z)]" etc.
def getPlotType(string: str) -> str:
    if   len(string) > 2 and string[0] == "(" and string[-1] == ")" and "," in string: return "POINT"
    elif len(string) > 4 and string[:2] == "[(" and string[-2:] == ")]" and "," in string: return "LINE"
    elif len(string) > 5 and string[0] == "P" and string[1:3] == "[(" and string[-2:] == ")]" and "," in string: return "POLYGON"
    elif len(string) > 4 and string[1] == "(" and string[3] == ")" and "=" in string: return "FUNCTION1"
    elif len(string) > 2 and string[0] == "y" and "=" in string: return "FUNCTION2"
    else: return "FUNCTION3"

# takes a string and converts it into the appropriate data for a plot.
# notice how the functionx typing gets put into use here to distinguish between different types of functions.
def convertStringToPlot(string: str):
    plotType = getPlotType(string)

    if   plotType == "POINT":
        data = [float(i) for i in string[1:-1].split(",")]
    elif plotType == "LINE":
        data = [[float(j) for j in i] for i in [i.split(",") for i in string[2:-2].split("),(")]]
    elif plotType == "POLYGON":
        data = [[float(j) for j in i] for i in [i.split(",") for i in string[3:-2].split("),(")]]
    elif plotType == "FUNCTION1":
        string = "".join([i.strip() for i in string.split("=")])
        data = eval("lambda " + string[2] + " : " + string[4:])
    elif plotType == "FUNCTION2":
        data = eval("lambda x : " + string.split("=")[1].strip(), {"__builtins__": {}}, safe_dict)
    else:
        data = eval("lambda x : " + string, {"__builtins__": {}}, safe_dict)
    
    # do some tests to make sure the data is correct and functional
    # test for functions is to test their values out
    if plotType in ["FUNCTION1", "FUNCTION2", "FUNCTION3"]:
        try:
            x = data(1)
            x = data(-1)
            x = data(7)
        except ArithmeticError:
            pass
    
    if plotType in ["LINE", "POLYGON"]:
        x = data[0]
        y = data[0][0]
        z = data[0][1]
    
    if plotType == "POINT":
        x = data[0]
        y = data[1]

    # if the program did all that without raising anything, our data is okay, return it
    return data

# takes a colour string and corrects it based on what kind of input it is.
def validateColour(colourString: str) -> str:
    # if it is a colour name, leave it alone.
    if colourString in ["red","orange","yellow","green","blue","purple","pink","magenta","cyan","brown","black","gray","white","teal","beige"]: return colourString
    
    # if it is a hexadecimal code with a hashtag, leave it alone.
    # the all function is a function that returns True only if all of its elements are True.
    if colourString[0] == "#" and all([i in "0123456789abcdefABCDEF" for i in colourString[1:]]) and len(colourString) == 7:
        return colourString

    # if the colour is a hex code without a hashtag, add one.
    if all([i in "0123456789abcdefABCDEF" for i in colourString]) and len(colourString) == 6:
        return "#" + colourString

    # if the input is an rgb input like "rgb(x, y, z)", convert it into hex.
    # this takes the three inputs,
    # converts them to hexadecimal
    # (with some additions to ensure leading zeroes and nonnegative values),
    # then removes the leading "0x" hexadecimal identifier,
    # joins them together, and adds the hashtag to the start.
    if colourString[:4] == "rgb(" and colourString[-1] == ")" and colourString.count(",") == 2:
        return "#"+"".join([hex(256 + abs(int(i)%256))[3:] for i in colourString[4:-1].split(",")])
    
    # if the input is ANYTHING ELSE, raise an error
    raise ValueError(colourString  + "is not a valid colour.")

# takes plot string, colour, and size. generates the correctly formatted dictionary.
def makePlotDictionary(plotString: str, plotColour: str = "#00A000", plotSize: int | float = 1) -> dict:
    return {
        "TYPE": getPlotType(plotString),
        "DATA": convertStringToPlot(plotString),
        "DISP": plotString,
        "COLR": validateColour(plotColour),
        "SIZE": plotSize,
        "VISB": True
    }

# takes a number and formats it nicely
def formatNumber(value: int | float) -> str:
    if value == 0: return "0"
    if abs(value) > 1e6 or abs(value) < 1e-2: return "{:.2e}".format(value).replace("+","")
    else: return "{:.2f}".format(value)

# ------------------------------------------------------------- #
# USER COMMANDS AND INPUT                                       #
# The commands the user can run as well as the parser for them. #
# ------------------------------------------------------------- #

"""
A QUICK OVERVIEW OF USER COMMANDS:

"""

# ----------------------------------------- #
# MAIN LOOP                                 #
# Runs the actual program as the main loop. #
# ----------------------------------------- #

window.mainloop()