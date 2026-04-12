#
# IMPORTS
#

import tkinter as tk
from turtle import TurtleScreen, RawTurtle
import math as m

#
# DEFINITIONS
#

# defines the bounds of the graph
# llx, lly : lower left x and y
# urx, ury : upper right x and y
# this approach is used because it's also used in the turtle module
graphBounds = {
    "llx" : -2,
    "lly" : -2,
    "urx" :  2,
    "ury" :  2
}

# defines the spatial resolution of the graph.
graphResolution = 0.02

def getGraphSize():
    """
    Returns the size of the graph's bounds.

    Returns:
        tuple: (x_size, y_size) the size of the graph along the axes.
    """
    return (graphBounds["urx"] - graphBounds["llx"], graphBounds["ury"] - graphBounds["lly"])

def updateBounds():
    """
    Updates the screen's world coordinates using graphBounds
    """
    graphScreen.setworldcoordinates(graphBounds["llx"], graphBounds["lly"], graphBounds["urx"], graphBounds["ury"])

def isValidColor(col):
    """
    Returns true if the colour is valid. A valid colour is either a hex code, or a descriptor like "blue" or "cyan".
    """
    return col[0] == "#" or col in ["red","orange","yellow","green","lime","cyan","blue","black","gray","white","brown","pink","purple"]


# defines the existing plots.
#
plots = []

#
# GUI CREATION
#

# create window
window = tk.Tk()
window.geometry("1400x1000")
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(1, weight=1)

# create canvas: the thing turtle will draw on
graphCanvas = tk.Canvas(width=1000, height=1000)
graphCanvas.grid(row=0,column=0,rowspan=2)

# create screen: the drawing surface of turtle.
graphScreen = TurtleScreen(graphCanvas)
graphScreen.tracer(0, 0) # manual updates only.
updateBounds()

graphTurtle = RawTurtle(graphScreen, visible=False) # create invisible turtle.

commandEntry = tk.Entry(window, width=50)
commandEntry.grid(row=0,column=1, sticky="nsew", padx=5, pady=5)

plotsListString = tk.StringVar(window)

plotsList = tk.Label(window, textvariable=plotsListString, font=("Courier New", 10), wraplength=350, justify="left")
plotsList.grid(row=1,column=1, sticky="nsew", padx=5, pady=5)

def updatePlotList():
    """
    Updates the StringVar describing the plots in the graph.
    """
    global plotsListString
    plotString = ""
    for id, plot in enumerate(plots):
        plotString += "ID: " + str(id) + " | Plot: " + plot["equ"] + "\n"
    plotsListString.set(plotString)
#
# PLOTTING
#

def getBestGrid():
    """
    Returns grid lines with nice spacing (1, 2, 5, 10, 20, 50, etc.) depending on the graph's bounds, and a smaller grid at 5x resolution

    Returns:
        tuple: (grid_x, grid_y, gridSmall_x, gridSmall_y) lists of grid line positions
    """
    # algorithm:
    # 

    # calculate ideal tick distance, which is 1/10th the size of the graph.
    dx = (graphBounds["urx"] - graphBounds["llx"])*0.1
    dy = (graphBounds["ury"] - graphBounds["lly"])*0.1

    dx, dy = getGraphSize()[0] * 0.1, getGraphSize()[1] * 0.1

    # sub-function that gets nearest nice value between 1 and 10
    def getNiceValue(x):
        if x < 1.5: return 1
        if x < 3.5: return 2
        if x < 7.5: return 5
        return 10
    
    # convert distances to exponent and mantissa.
    exponent_x = m.floor(m.log10(dx))
    mantissa_x = dx*(0.1)**(exponent_x)

    exponent_y = m.floor(m.log10(dy))
    mantissa_y = dy*(0.1)**(exponent_y)

    # turn the mantissas into nice values
    mantissa_x = getNiceValue(mantissa_x)
    mantissa_y = getNiceValue(mantissa_y)
    
    # reconstruct nice values for dx and dy
    nice_dx = 10**exponent_x * mantissa_x
    nice_dy = 10**exponent_y * mantissa_y

    # calculate the minimum position of the grids
    minGrid_x = m.floor(graphBounds["llx"]/nice_dx)*nice_dx
    minGrid_y = m.floor(graphBounds["lly"]/nice_dy)*nice_dy

    # calculate the number of gridlines needed
    gridCount_x = m.floor((graphBounds["urx"]-minGrid_x)/nice_dx)
    gridCount_y = m.floor((graphBounds["ury"]-minGrid_y)/nice_dy)

    # generate the actual grid points
    grid_x = [minGrid_x + i*nice_dx for i in range(gridCount_x)]
    grid_y = [minGrid_y + i*nice_dy for i in range(gridCount_y)]

    # generate small grid points
    gridSmall_x = []
    gridSmall_y = []
    for d in [0, 0.2, 0.4, 0.6, 0.8]:
        gridSmall_x += [minGrid_x + (i+d)*nice_dx for i in range(gridCount_x)]
        gridSmall_y += [minGrid_y + (i+d)*nice_dy for i in range(gridCount_y)]

    # return as a tuple
    return (grid_x, grid_y, gridSmall_x, gridSmall_y)

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

    # remove the center from the grids, since there is a section to draw it that the axes would do wrong
    # try to catch if zero is not present. this will change if certain aspects of the graph are drawn.
    try:
        centerExistsFlag = True
        grid_x.remove(0)
        grid_y.remove(0)
        gridSmall_x.remove(0)
        gridSmall_y.remove(0)
    except ValueError:
        centerExistsFlag = False

    # y-axis
    graphTurtle.pencolor("#0000FF")
    graphTurtle.teleport(axisDraw_x, graphBounds["lly"])
    graphTurtle.goto(    axisDraw_x, graphBounds["ury"])

    # y-axis ticks
    for y in grid_y:
        graphTurtle.teleport(axisDraw_x-getGraphSize()[0]*0.017, y)
        graphTurtle.goto(    axisDraw_x+getGraphSize()[0]*0.017, y)
        graphTurtle.write(y)

    # small y-axis ticks
    for y in gridSmall_y:
        graphTurtle.teleport(axisDraw_x-getGraphSize()[0]*0.007, y)
        graphTurtle.goto(    axisDraw_x+getGraphSize()[0]*0.007, y)

    # x-axis
    graphTurtle.pencolor("#FF0000")
    graphTurtle.teleport(graphBounds["llx"], axisDraw_y)
    graphTurtle.goto(    graphBounds["urx"], axisDraw_y)

    # x-axis ticks
    for x in grid_x:
        graphTurtle.teleport(x, axisDraw_y-getGraphSize()[1]*0.017)
        graphTurtle.goto(    x, axisDraw_y+getGraphSize()[1]*0.017)
        graphTurtle.write(x)

    # small x-axis ticks
    for x in gridSmall_x:
        graphTurtle.teleport(x, axisDraw_y-getGraphSize()[1]*0.007)
        graphTurtle.goto(    x, axisDraw_y+getGraphSize()[1]*0.007)

    # draw centre of graph
    if centerExistsFlag:
        graphTurtle.pencolor("#000000")
        graphTurtle.pensize(2)
        graphTurtle.teleport(axisDraw_x, axisDraw_y-getGraphSize()[0]*0.017)
        graphTurtle.goto(    axisDraw_x, axisDraw_y+getGraphSize()[0]*0.017)
        graphTurtle.teleport(axisDraw_x-getGraphSize()[0]*0.017, axisDraw_y)
        graphTurtle.goto(    axisDraw_x+getGraphSize()[0]*0.017, axisDraw_y)
        graphTurtle.pensize(1)

def evaluateType(plotText):
    """
    Evaluates the type of plot that the user has inputted. There are three types: function, point, list of points (polygon).

    Returns:
        tuple: (plotType, convertedPlot)
    """

    # Conditions for a plot being a function: has the form "f(*) = ...", and * is the character to evaluate. f can be another letter. it can also be of the form "y = *".
    # Conditions for a plot being a point: has the form "(*,*)"
    # Conditions for a plot being a list of points (polygon): has the form "[(*,*),(*,*)...]"

    if len(plotText) >= 3:
        if plotText[0] == "y":
            functionValue = plotText[plotText.index("=")+1:].strip()
            functionInput = "x"
            return ("lambda x : " + functionValue, "function")
        
        if plotText[0] == "(" and plotText[-1] == ")":
            return (plotText, "point")
        
        if plotText[0:2] == "[(" and plotText[-2:] == ")]":
            return (plotText, "polygon")
        
        if plotText[1] == "(" and plotText[3] == ")":
            functionInput = plotText[2]
            functionValue = plotText[plotText.index("=")+1:].strip()
            return ("lambda " + functionInput + " : " + functionValue, "function")
        
    # default case, just pretend the variable is x.
    functionInput = "x"
    functionValue = plotText
    return ("lambda x : " + functionValue, "function")

def drawPlotFunction(plot):
    """
    Draws the points of a plotted function.
    """
    loBound = graphBounds["llx"]
    hiBound = graphBounds["urx"]
    resolution = getGraphSize()[0]*graphResolution

    f = eval(plot["equ"], {**vars(m), "__builtins__": __builtins__})
    x = loBound
    graphTurtle.pencolor(plot["col"])
    graphTurtle.pensize(plot["size"])
    graphTurtle.teleport(x, f(x))
    while x < hiBound:
        x += resolution
        try:
            graphTurtle.goto(x, f(x))
        except:
            graphTurtle.goto(x, 0)
    
    graphTurtle.pencolor("#000000")
    graphTurtle.pensize(1)

    graphScreen.update()

def drawPlotPoint(plot):
    """
    Draws the points of a plotted point.
    """


def drawGraph():
    """
    Draws a full graph, including the plots, points, and polygons.
    """
    graphTurtle.clear()

    drawGrid()

    for plot in plots:
        if plot["type"] == "function": drawPlotFunction(plot)

    graphScreen.update()

def moveGraph(dx, dy):
    """
    Moves the graph by dx in the x direction and by dy in the y direction.
    """
    # adjust bounds
    graphBounds["llx"] += dx
    graphBounds["urx"] += dx
    graphBounds["lly"] += dy
    graphBounds["ury"] += dy
    updateBounds()

    drawGraph() # update graph.


def scaleGraph(scale_x, scale_y):
    """
    Scales the graph by scale_x in the x direction and by scale_y in the y direction
    """
    # adjust bounds
    graphBounds["llx"] *= scale_x
    graphBounds["urx"] *= scale_x
    graphBounds["lly"] *= scale_y
    graphBounds["ury"] *= scale_y
    updateBounds()

    drawGraph() # update graph.

#
# GRAPH COMMANDS
#

def moveGraphCommand(args):
    """
    Moves the graph with the first and second argument.
    """
    arg_dx = float(args[0])
    arg_dy = float(args[1])

    moveGraph(arg_dx, arg_dy)

def scaleGraphCommand(args):
    """
    Scales the graph by the first the first argument in both directions, or by the first argument in the x direction and by the second argument in the y direction.
    """

    # this try-except block essentially checks if there really is a second argument, and applies the correct version of the command.
    try:
        argScale_x = float(args[0])
        argScale_y = float(args[1])
        scaleGraph(argScale_x, argScale_y)
    except IndexError:
        scaleGraph(argScale_x, argScale_x)


def exitGraph():
    """
    Exits the program (destroys the main window).
    """
    window.destroy()

def initialiseGraphCommand(args):
    """
    Initialises certain aspects of the graph. if the input has "s" in initialises scale, if the input has "c", it re-centers the graph, and if the input has "p", it initialises the plots.
    """
    global graphBounds
    global plots
    args_joined = "".join(args)
    graphCenter_x = graphBounds["urx"]*0.5 + graphBounds["llx"]*0.5
    graphCenter_y = graphBounds["ury"]*0.5 + graphBounds["lly"]*0.5
    graphSize_x, graphSize_y = getGraphSize()

    if args_joined == "":
        args_joined = "scp"

    if "s" in args_joined:
        graphBounds = {
            "llx" : graphCenter_x-2,
            "lly" : graphCenter_y-2,
            "urx" : graphCenter_x+2,
            "ury" : graphCenter_y+2
        }
        updateBounds()
        graphSize_x, graphSize_y = 4, 4
    
    if "c" in args_joined:
        graphBounds = {
            "llx" : -graphSize_x * 0.5,
            "lly" : -graphSize_y * 0.5,
            "urx" :  graphSize_x * 0.5,
            "ury" :  graphSize_y * 0.5
        }
        updateBounds()
        graphCenter_x, graphCenter_y = 0, 0
    
    if "p" in args_joined:
        plots = []
    
    updatePlotList()
    drawGraph()

def addPlotCommand(args):
    """
    Inserts a plot into the graph. Takes in three arguments (at most): The plot, the colour, and thickness.
    """
    global plots
    plotType = evaluateType(args[0])[1]
    plotText = evaluateType(args[0])[0]
    if len(args) == 1:
        plot = {
            "equ"  : plotText,
            "type" : plotType,
            "col"  : "#008000",
            "size" : 1
        }
    if len(args) == 2:
        plot = {
            "equ"  : plotText,
            "type" : plotType,
            "col"  : args[1],
            "size" : 1
        }
    if len(args) == 3:
        plot = {
            "equ"  : plotText,
            "type" : plotType,
            "col"  : args[1],
            "size" : float(args[2])
        }
    
    try:
        plots.append(plot)
        updatePlotList()
        drawGraph()
    except:
        plots.pop()  # remove the plot if drawing failed
        updatePlotList()
        return

def removePlotCommand(args):
    """
    Removes a plot based on its ID (its position in the plots list).
    """
    global plots
    try:
        plots.pop(int(args[0]))
        updatePlotList()
        drawGraph()
    except:
        return

def setResolutionCommand(args):
    """
    Sets the graphResolution variable to a given value.
    """
    global graphResolution
    try:
        graphResolution = float(args[0])
        drawGraph()
    except:
        return
#
# RUNTIME (AND TESTING)
#

def enter_command(entry=None):
    """
    Takes commands from the entry line and sends them to the correct graph command.
    """
    command = commandEntry.get().split()[0]
    args = commandEntry.get().split()[1:]

    if command in ["move","mv"]: moveGraphCommand(args)
    if command in ["scale","sc"]: scaleGraphCommand(args)
    if command in ["init","it"]: initialiseGraphCommand(args)
    if command in ["plot","pt"]: addPlotCommand(args)
    if command in ["exit","ex"]: exitGraph()
    if command in ["remove","rm"]: removePlotCommand(args)
    if command in ["setres","sr"]: setResolutionCommand(args)
    commandEntry.delete(0, tk.END)
window.bind("<Return>", enter_command)

drawGrid()

window.mainloop()