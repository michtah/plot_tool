# revised version of the original program, as the original version was relatively unorganised.

# * ----------------------------------------------------------------------------------------------- #
# * IMPORTS                                                                                         #
# * The external packages that plot_tool uses. All of these come with a default python installation #
# * ----------------------------------------------------------------------------------------------- #

import tkinter as tk
from turtle import TurtleScreen, RawTurtle
import math as m

# * ---------------------------------------------------------------- #
# * DEFINITIONS                                                      #
# * Defines variables that the program uses throughout its existence #
# * ---------------------------------------------------------------- #

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
safe_dict = {"__builtins__": {}, **safe_dict}

# this is the help string
# it holds the information that the help command and the more command display
helpString = ""

# * --------------------------------- #
# * GRAPHICS                          #
# * Defines the graphics for the plot #
# * --------------------------------- #

# Create window and set size.
window = tk.Tk()
window.geometry("1500x1000")
window.title("Plot Tool")

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
errorLabel = tk.Label(window, textvariable=errorString, font=("Courier New", 9), wraplength=350, justify="left", height=2, fg="red", anchor="w") # create label that displays the plot information
errorLabel.grid(row=1, column=1, padx=2, pady=1, sticky="ew") # place this label

# plot list
plotsString = tk.StringVar(window, value="Plots:")
plotsLabel = tk.Label(window, textvariable=plotsString, font=("Courier New", 9), wraplength=350, justify="left", height=1, anchor="nw")
plotsLabel.grid(row=2,column=1, padx=2, pady=1, sticky="nsew")

# general graph info
infoString = tk.StringVar(window, value="Graph Info:") # create string variable to store plot information
infoLabel = tk.Label(window, textvariable=infoString, font=("Courier New", 9, "italic"), wraplength=350, justify="left", height=1, anchor="w") # create label that displays the plot information
infoLabel.grid(row=3,column=1, padx=2, pady=5, sticky="ew") # place this label

# * ------------------------------------ #
# * DEFINITION AND GUI HELPERS           #
# * Functions to get and set definitions #
# * Functions to modify the GUI          #
# * ------------------------------------ #

# returns the graph's dimensions (x,y) as a tuple.
def getGraphDimensions() -> tuple[float, float]:
    global graphBounds
    return (graphBounds["urx"] - graphBounds["llx"], graphBounds["ury"] - graphBounds["lly"])

# returns the centre of the graph as a tuple.
def getGraphCentre() -> tuple[float, float]:
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

# changes the display of the plot info to a custom string, not the automatically generated plot information
# this is used by the help command to display information instead of the plot information
def displayPlotsCustom(string):
    plotsString.set(string)


# * --------------------------------------------------------- #
# * HELPERS                                                   #
# * Helper functions that aren't commands the user can access #
# * --------------------------------------------------------- #

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
        data = eval("lambda " + string[2] + " : " + string[4:], safe_dict)
    elif plotType == "FUNCTION2":
        data = eval("lambda x : " + string.split("=")[1].strip(), safe_dict)
    else:
        data = eval("lambda x : " + string, safe_dict)
    
    # do some tests to make sure the data is correct and functional
    # test for functions is to test their values out
    # we ignore arithmetic issues because partial plots are no problem for the plotter
    # parts of the plot can have undefined values
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
    if colourString in ["red","orange","yellow","green","blue","purple","pink","magenta","cyan","brown","black","gray","white","teal","beige","grey"]: return colourString
    
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
    raise ValueError(colourString  + " is not a valid colour")

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

# checks the validity of indices compared to the plot list.
def validIndex(*args):
    global plots
    return all(index >= 0 and index < len(plots) for index in args)

# this function takes a list of strings that describe possible inputs
# and a string that contains the user input
# and parses the user input using the descriptive strings.

# the format of the strings are as follows:
# a name, followed by a colon, followed by a type
# these are separated by spaces
# the name is the name of that specific input, 
# and the type description afterwards tells the function 
# what kind of input it should expect (for this program: float, int, plot id, or str)

# it also raises appropriate errors if there are issues
# * this function isn't used by the plotting functions as they have
# * a different syntax for parsing their inputs

def parseInput(inputTypesString: list[str] | str, userInput: str):
    if type(inputTypesString) == str: inputTypesString = [inputTypesString]
    # split the input types and the user input
    inputNames = [[i.split(":")[0] for i in S.split()] for S in inputTypesString]
    inputTypes = [[i.split(":")[1] for i in S.split()] for S in inputTypesString]
    userInputs = userInput.split()

    # calculate number of arguments possible and number of arguments given by user
    validArgCounts = [len(inputType) for inputType in inputTypes]
    userInputArgCount = len(userInputs)

    # generate preset string describing possible number of inputs
    if len(validArgCounts) == 1:
        if validArgCounts[0] == 1:
            validArgCountsString = str(validArgCounts[0]) + " argument"
        else:
            validArgCountsString = str(validArgCounts[0]) + " arguments"
    else:
        validArgCountsString = ", ".join([str(argCount) for argCount in validArgCounts[:-1]]) + " or " + str(validArgCounts[-1]) + " arguments"
    # generate dictionary to convert between shorthand single letter types and long type names
    longTypeNames = {
        "i":"integer",
        "d":"plot ID",
        "f":"real value",
        "s":"string"
    }

    
    # if there is a mismatch between number of inputs expected and number of inputs given, raise a syntax error.
    if userInputArgCount not in validArgCounts:
        raise SyntaxError("Expected " + validArgCountsString + " but got " + str(userInputArgCount) + ".")
    
    # otherwise, find the inputType we should use for the number of arguments we have
    # in other situations I'd care about differentiating different input types that
    # have the same number of arguments but
    # this case never happens in our commands so it is not needed
    inputName = inputNames[validArgCounts.index(userInputArgCount)]
    inputType = inputTypes[validArgCounts.index(userInputArgCount)]

    # create the output list
    outputList = []

    # we create a for loop using the zip function
    # so i can have access to a tuple for each step containing
    # the input name, input type, and user name
    for argName, argType, argUser in zip(inputName, inputType, userInputs):
        # try to convert
        try:
            argCurrent = argUser
            if argType == "i":
                argCurrent = int(argUser)
            elif argType == "d":
                argCurrent = int(argUser)
                if not validIndex(argCurrent):
                    raise IndexError(argName + " out of bounds.")
            elif argType == "f":
                argCurrent = float(argUser)
            elif argType == "s":
                argCurrent = str(argCurrent)
            else:
                raise Exception("parseInput failed: argType was not 'i', 'f' or 's'.")
            outputList.append(argCurrent)
        # if it fails, we'll raise the value error with some info about what went wrong
        except ValueError:
            raise ValueError("Can't convert input " + argName + " to type " + longTypeNames[argType] + ".")

    # if conversion is successful, return the list of outputs
    return outputList

# * ------------------------------------ #
# * PLOTTING AND RENDERING               #
# * The tools that plot the actual graph #
# * ------------------------------------ #

# returns grid lines with good spacing based on the size of the grid.
def getBestGrid() -> list[float | int]:
    # calculate ideal tick distance, which is 1/10th the size of the graph.
    dx, dy = getGraphDimensions()[0] * 0.1, getGraphDimensions()[1] * 0.1

    # this sub-function gets nicest value for a tick between 1 and 10
    # this is scaled by powers of ten to get the whole range of valid numbers
    def getNiceValue(x):
        if x < 1.5: return 1
        if x < 3.5: return 2
        if x < 7.5: return 5
        return 10
    
    # we use python's scientific notation formatting to extract the exponent and mantissa
    mantissa_x, exponent_x = [float(i) for i in "{:.10e}".format(dx).split("e")]
    mantissa_y, exponent_y = [float(i) for i in "{:.10e}".format(dy).split("e")]

    # then, reconstruct the nice values for dx and dy using this information
    nice_dx = 10**exponent_x * getNiceValue(mantissa_x)
    nice_dy = 10**exponent_y * getNiceValue(mantissa_y)

    # generate large grids
    grid_x = [round(graphBounds["llx"]/nice_dx)*nice_dx + i*nice_dx for i in range(int((graphBounds["urx"]-graphBounds["llx"])/nice_dx)+1)]
    grid_y = [round(graphBounds["lly"]/nice_dy)*nice_dy + i*nice_dy for i in range(int((graphBounds["ury"]-graphBounds["lly"])/nice_dy)+1)]

    # generate small grids
    gridSmall_x = [j for i in [[i + nice_dx*p for i in grid_x] for p in [0.2, 0.4, 0.6, 0.8]] for j in i]
    gridSmall_y = [j for i in [[i + nice_dy*p for i in grid_y] for p in [0.2, 0.4, 0.6, 0.8]] for j in i]

    # return as list of the grids with values that equal zero removed
    return [[x for x in grid if x != 0] for grid in [grid_x, grid_y, gridSmall_x, gridSmall_y]]


# draws the grid onto the screen
def drawGrid():
    """
    Draws the grid onto the screen and updates it.
    """
    
    grid_x, grid_y, gridSmall_x, gridSmall_y = getBestGrid() # unpack grid

    # draw the small grid
    graphTurtle.pencolor("#DDDDDD")
    for x in gridSmall_x:
        graphTurtle.teleport(x, graphBounds["lly"])
        graphTurtle.goto(    x, graphBounds["ury"])
    
    for y in gridSmall_y:
        graphTurtle.teleport(graphBounds["llx"], y)
        graphTurtle.goto(    graphBounds["urx"], y)

    # draw the regular grid
    graphTurtle.pencolor("#AAAAAA")
    for x in grid_x:
        graphTurtle.teleport(x, graphBounds["lly"])
        graphTurtle.goto(    x, graphBounds["ury"])
    
    for y in grid_y:
        graphTurtle.teleport(graphBounds["llx"], y)
        graphTurtle.goto(    graphBounds["urx"], y)

    # draw the axes and the ticks
    # if the axis is out of bounds, draw it on one of the edges instead.

    axisDraw_x = min(max(0, graphBounds["llx"]), graphBounds["urx"])
    axisDraw_y = min(max(0, graphBounds["lly"]), graphBounds["ury"])

    # see if the centre is contained in the graph bounds. this will affect how we draw the graph.
    centreExistsFlag = not(graphBounds["llx"] > 0 or graphBounds["urx"] < 0 or graphBounds["lly"] > 0 or graphBounds["ury"])

    # y-axis
    graphTurtle.pencolor("#0000FF")
    graphTurtle.teleport(axisDraw_x, graphBounds["lly"])
    graphTurtle.goto(    axisDraw_x, graphBounds["ury"])

    # y-axis ticks
    for y in grid_y:
        graphTurtle.teleport(axisDraw_x-getGraphDimensions()[0]*0.017, y)
        graphTurtle.goto(    axisDraw_x+getGraphDimensions()[0]*0.017, y)
        graphTurtle.write(y)

    # small y-axis ticks
    for y in gridSmall_y:
        graphTurtle.teleport(axisDraw_x-getGraphDimensions()[0]*0.007, y)
        graphTurtle.goto(    axisDraw_x+getGraphDimensions()[0]*0.007, y)

    # x-axis
    graphTurtle.pencolor("#FF0000")
    graphTurtle.teleport(graphBounds["llx"], axisDraw_y)
    graphTurtle.goto(    graphBounds["urx"], axisDraw_y)

    # x-axis ticks
    for x in grid_x:
        graphTurtle.teleport(x, axisDraw_y-getGraphDimensions()[1]*0.017)
        graphTurtle.goto(    x, axisDraw_y+getGraphDimensions()[1]*0.017)
        graphTurtle.write(x)

    # small x-axis ticks
    for x in gridSmall_x:
        graphTurtle.teleport(x, axisDraw_y-getGraphDimensions()[1]*0.007)
        graphTurtle.goto(    x, axisDraw_y+getGraphDimensions()[1]*0.007)

    # draw centre of graph
    if centreExistsFlag:
        graphTurtle.pencolor("#000000")
        graphTurtle.pensize(2)
        graphTurtle.teleport(axisDraw_x, axisDraw_y-getGraphDimensions()[0]*0.017)
        graphTurtle.goto(    axisDraw_x, axisDraw_y+getGraphDimensions()[0]*0.017)
        graphTurtle.teleport(axisDraw_x-getGraphDimensions()[0]*0.017, axisDraw_y)
        graphTurtle.goto(    axisDraw_x+getGraphDimensions()[0]*0.017, axisDraw_y)
        graphTurtle.pensize(1)


# draws a function plot
def drawFunction(func: function, colour: str, size: float | int):
    graphTurtle.pencolor(colour)
    graphTurtle.pensize(size)
    x = graphBounds["llx"] - graphResolution
    try:
        graphTurtle.teleport(x, func(x))
    except ArithmeticError, tk.TclError:
        graphTurtle.teleport(x, 0)
    
    while x < graphBounds["urx"]:
        x += graphResolution
        try:
            graphTurtle.goto(x, func(x))
        except ArithmeticError:
            graphTurtle.teleport(x, 0)
    
    graphTurtle.pencolor("#000000")
    graphTurtle.pensize(1)


# draws a point plot
def drawPoint(point: tuple[float | int, float | int], colour: str, size: float | int):
    graphTurtle.pencolor(colour)
    graphTurtle.pensize(size*5)

    graphTurtle.teleport(point[0] + graphResolution, point[1])
    graphTurtle.goto(    point[0], point[1] + graphResolution)
    graphTurtle.goto(    point[0] - graphResolution, point[1])
    graphTurtle.goto(    point[0], point[1] - graphResolution)

    graphTurtle.pencolor("#000000")
    graphTurtle.pensize(1)


# draws a line
def drawLine(pointList: list[tuple], colour: str, size: float | int):
    graphTurtle.pencolor(colour)
    graphTurtle.pensize(size)

    graphTurtle.teleport(pointList[0][0],pointList[0][1])
    for point in pointList[1:]:
        graphTurtle.goto(point[0],point[1])

    graphTurtle.pencolor("#000000")
    graphTurtle.pensize(1)


# draws a polygon
def drawPolygon(pointList: list[tuple], colour: str, size: float | int):
    graphTurtle.pencolor(colour)
    graphTurtle.pensize(size)

    graphTurtle.teleport(pointList[0][0],pointList[0][1])
    for point in pointList[1:]:
        graphTurtle.goto(point[0],point[1])
    
    graphTurtle.goto(pointList[0][0],pointList[0][1])

    graphTurtle.pencolor("#000000")
    graphTurtle.pensize(1)

# full rendering, including updating text
def drawGraph():
    global plots
    graphTurtle.clear() # clear screen
    updateBounds() # update the bounds of the plot as they may have changed
    drawGrid() # draw the grid again
    for plot in plots: # draw each plot
        if not plot["VISB"]: continue # if the plot is invisible, skip
        else:
            if plot["TYPE"] in ["FUNCTION1", "FUNCTION2", "FUNCTION3"]:
                drawFunction(plot["DATA"], plot["COLR"], plot["SIZE"])
            elif plot["TYPE"] == "POINT":
                drawPoint(plot["DATA"], plot["COLR"], plot["SIZE"])
            elif plot["TYPE"] == "LINE":
                drawLine(plot["DATA"], plot["COLR"], plot["SIZE"])
            elif plot["TYPE"] == "POLYGON":
                drawPolygon(plot["DATA"], plot["COLR"], plot["SIZE"])
    
    graphScreen.update()
    displayInfo()
    displayPlots()

# * ------------------------------------------------------------ #
# * USER COMMANDS AND INPUT                                      #
# * The commands the user can run as well as the parser for them #
# * ------------------------------------------------------------ #


# plot command. takes in one required input, which is the plot function / list / point
def plotCommand(userParameters):
    global plots
    # see if the user has provided a valid input for the command to parse.
    if userParameters == "":
        raise SyntaxError("Provide at least plot data (and optionally colour and size)")
    # if there are any, the parameters are extracted into a list
    extractedParameters = [i.strip() for i in userParameters.split("~")]
    if len(extractedParameters) == 1:
        plotParameter = extractedParameters[0]
        plots.append(makePlotDictionary(plotParameter))
    if len(extractedParameters) == 2:
        plotParameter = extractedParameters[0]
        colourParameter = extractedParameters[1]
        plots.append(makePlotDictionary(plotParameter, colourParameter))
    if len(extractedParameters) > 2:
        plotParameter = extractedParameters[0]
        colourParameter = extractedParameters[1]
        sizeParameter = extractedParameters[2]
        plots.append(makePlotDictionary(plotParameter, colourParameter, sizeParameter))

def plotsCommand(userParameters):
    global plots
    
    # see if the user has provided a valid input for the command to parse.
    if userParameters == "":
        raise SyntaxError("Provide at least plot data (and optionally colour and size)")
    # if there are any, the parameters are extracted into a list
    extractedParameters = [i.strip() for i in userParameters.split("~")]
    if len(extractedParameters) == 1:
        plotParameters = [i.strip() for i in extractedParameters[0].split(";")]
        for plotParameter in plotParameters:
            plots.append(makePlotDictionary(plotParameter))
    if len(extractedParameters) == 2:
        plotParameters = [i.strip() for i in extractedParameters[0].split(";")]
        colourParameter = extractedParameters[1]
        for plotParameter in plotParameters:
            plots.append(makePlotDictionary(plotParameter, colourParameter))
    if len(extractedParameters) > 2:
        plotParameters = [i.strip() for i in extractedParameters[0].split(";")]
        colourParameter = extractedParameters[1]
        sizeParameter = extractedParameters[2]
        for plotParameter in plotParameters:
            plots.append(makePlotDictionary(plotParameter, colourParameter, sizeParameter))


def moveCommand(userParameters):
    global graphBounds
    dx, dy = parseInput("dx:f dy:f", userParameters)

    graphBounds["llx"] += dx
    graphBounds["lly"] += dy
    graphBounds["urx"] += dx
    graphBounds["ury"] += dy


def scaleCommand(userParameters):
    global graphBounds
    args = parseInput(["scale:f", "scale_x:f scale_y:f"], userParameters)
    if len(args) == 1: scale_x, scale_y = args[0], args[0]
    else: scale_x, scale_y = args
    
    # the scaling should be around the center, not just the graph bounds, so we need to find the center and also the dimensions
    graphDim_x, graphDim_y = getGraphDimensions()
    graphCen_x, graphCen_y = getGraphCentre()

    graphBounds["llx"] = graphCen_x - graphDim_x * scale_x * 0.5
    graphBounds["lly"] = graphCen_y - graphDim_y * scale_y * 0.5
    graphBounds["urx"] = graphCen_x + graphDim_x * scale_x * 0.5
    graphBounds["ury"] = graphCen_y + graphDim_y * scale_y * 0.5


def setboundsCommand(userParameters):
    global graphBounds
    args = parseInput(["a:f", "a:f b:f", "a:f b:f c:f d:f"], userParameters)
    if len(args) == 1:
        graphBounds = {"llx": -args[0], "lly": -args[0], "urx": args[0], "ury": args[0]}
    if len(args) == 2:
        graphBounds = {"llx": -args[0], "lly": -args[1], "urx": args[0], "ury": args[1]}
    if len(args) == 4:
        graphBounds = {"llx": args[0], "lly": args[1], "urx": args[2], "ury": args[3]}


def colourCommand(userParameters):
    global plots
    plotIndex, plotColour = parseInput("ID:d Colour:s", userParameters)
    
    # change the colour of the plot with id plotIndex to the colour plotColour
    plots[plotIndex]["COLR"] = validateColour(plotColour)
    

def sizeCommand(userParameters):
    global plots
    plotIndex, plotSize = parseInput("ID:d Size:f", userParameters)
    
    # change thickness of the plot with id plotIndex to plotSize.
    plots[plotIndex]["SIZE"] = plotSize


def swapCommand(userParameters):
    global plots
    plotIndex_1, plotIndex_2 = parseInput("ID_1:d ID_2:d", userParameters)

    # swap the two plots
    plots[plotIndex_1], plots[plotIndex_2] = plots[plotIndex_2], plots[plotIndex_1]


def toggleCommand(userParameters):
    plotIndex = parseInput("ID:d", userParameters)[0]

    # set the visibility of the plot to false.
    plots[plotIndex]["VISB"] = not plots[plotIndex]["VISB"]


def backCommand(userParameters):
    global plots
    args = parseInput(["ID:d", "ID:d Back:i"], userParameters)
    if len(args) == 1: plotIndex, backAmount = args[0], 1
    else: plotIndex, backAmount = args
        
    # check if index is last already. if it is raise an error.
    if plotIndex == len(plots) - 1: raise IndexError("Plot is already last")

    # clamp movement to not escape out of range
    backIndex = min(len(plots), plotIndex + backAmount + 1)
    
    plots = plots[:plotIndex] + plots[plotIndex+1:backIndex] + plots[plotIndex:plotIndex+1] + plots[backIndex:]


def frontCommand(userParameters):
    global plots
    args = parseInput(["ID:d", "ID:d Front:i"], userParameters)
    if len(args) == 1: plotIndex, frontAmount = args[0], 1
    else: plotIndex, frontAmount = args
        
    # check if index is first already. if it is raise an error.
    if plotIndex == 0: raise IndexError("Plot is already first")

    # clamp movement to range to not escape out of range
    frontIndex = max(0, plotIndex - frontAmount)

    plots = plots[:frontIndex] + plots[plotIndex:plotIndex+1] + plots[frontIndex:plotIndex] + plots[plotIndex+1:]


def removeCommand(userParameters):
    global plots
    args = parseInput(["Remove:d", "Remove_start:d Remove_end:d"], userParameters)
    if len(args) == 1: startIndex, endIndex = (args[0], args[0])
    else: startIndex, endIndex = args

    plots = plots[:startIndex] + plots[endIndex+1:]


def removeallCommand(userParameters):
    global plots
    plots = []


def resetposCommand(userParameters):
    # find dimensions. the graph will keep the same size but reset the middle values ot zero.
    graphDim_x, graphDim_y = getGraphDimensions()
    graphBounds["llx"] = -0.5*graphDim_x
    graphBounds["lly"] = -0.5*graphDim_y
    graphBounds["urx"] =  0.5*graphDim_x
    graphBounds["ury"] =  0.5*graphDim_y


def resetscaleCommand(userParameters):
    # find centre. the graph will keep the centre but reset the size to be 4x4.
    graphCentre_x, graphCentre_y = getGraphCentre()
    graphBounds["llx"] = 2 - graphCentre_x
    graphBounds["lly"] = 2 - graphCentre_y
    graphBounds["urx"] = 2 + graphCentre_x
    graphBounds["ury"] = 2 + graphCentre_y


def resetgraphCommand(userParameters):
    # set it back to its initial value
    global graphBounds
    graphBounds = {
        "llx" : -2,
        "lly" : -2,
        "urx" :  2,
        "ury" :  2
    }

def initCommand(userParameters):
    global graphBounds, plots
    graphBounds = {
        "llx" : -2,
        "lly" : -2,
        "urx" :  2,
        "ury" :  2
    }
    plots = []


def setresCommand(userParameters):
    global graphResolution
    newResolution = parseInput("Resolution:f", userParameters)[0]
    
    graphResolution = newResolution

def exitCommand(userParameters):
    window.destroy()
    exit()

def helpCommand(userParameters):
    return

def moreCommand(userParameters):
    return

# parses user input and runs the appropriate command
def runUserInput(userInput):
    userInput = commandEntry.get()
    userInput = userInput.split(" ", 1) # split into command and arguments string
    userCommand = userInput[0]

    # list of valid commands
    validCommands = ["plot", "pl", "move", "mv", "scale", "sc", "colour", "color", "cl", "size", "sz", "swap", "sw", "back", "bk", "front", "fr", "remove", "rm", "removeall", "ra", "resetpos", "rp", "resetscale", "rs", "resetgraph", "rg", "init", "ii", "setres", "sr", "help", "exit", "quit",  "toggle", "tg", "plotmany", "pm", "setbounds", "sb"]
    
    # take the user input for the command. if it doesn't exist (some commands have no inputs after all), give a default blank string instead
    try:
        userParameters = userInput[1]
    except IndexError:
        userParameters = ""

    # a dictionary with keyword-function pairs, associating the function with the appropriate keywords
    commandKeywordPairs = {
        "plot" : plotCommand, "pl": plotCommand,
        "plotmany": plotsCommand, "pm": plotsCommand,
        "move": moveCommand, "mv": moveCommand,
        "scale": scaleCommand, "sc": scaleCommand,
        "setbounds": setboundsCommand, "sb": setboundsCommand,
        "colour": colourCommand, "color": colourCommand, "cl": colourCommand,
        "size": sizeCommand, "sz": sizeCommand,
        "swap": swapCommand, "sw": swapCommand,
        "toggle": toggleCommand, "tg": toggleCommand,
        "back": backCommand, "bk": backCommand,
        "front": frontCommand, "fr": frontCommand,
        "remove": removeCommand, "rm": removeCommand,
        "removeall": removeallCommand, "ra": removeallCommand,
        "resetpos": resetposCommand, "rp": resetposCommand,
        "resetscale": resetscaleCommand, "rs": resetscaleCommand,
        "resetgraph": resetgraphCommand, "rg": resetgraphCommand,
        "init": initCommand, "ii": initCommand,
        "setres": setresCommand, "sr": setresCommand,
        "help": helpCommand,
        "exit": exitCommand, "quit": exitCommand
    }
    
    if userCommand not in validCommands:
        displayError("Command is invalid. Type \"help\" to view a list of commands.")
    else:
        try: commandKeywordPairs[userCommand](userParameters)
        except Exception as exc:
            if hasattr(exc, "message"): displayError(exc.message)
            else: displayError(exc)
        
    # update graph UI after running command
    drawGraph()

    # if the command is a help or more command,
    # manually update the plot information section
    # using the help string that these functions set
    displayPlotsCustom(helpString)

    
    # clear entry point
    commandEntry.delete(0, tk.END)
# bind the enter key to run the user input
window.bind("<Return>", runUserInput)


# ! ---------------------------------------- #
# ! MAIN LOOP                                #
# ! Runs the actual program as the main loop #
# ! ---------------------------------------- #

drawGraph()
window.mainloop()