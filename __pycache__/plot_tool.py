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


# defines the existing plots.
#
plots = []

#
# GUI CREATION
#

# create window
window = tk.Tk()
window.geometry("1400x1000")

# create canvas: the thing turtle will draw on
graphCanvas = tk.Canvas(width=1000, height=1000)
graphCanvas.place(x=0, y=0)

# create screen: the drawing surface of turtle.
graphScreen = TurtleScreen(graphCanvas)
graphScreen.tracer(0, 0) # manual updates only.
updateBounds()

graphTurtle = RawTurtle(graphScreen, visible=False) # create invisible turtle.

commandEntry = tk.Entry(window, width=400)
commandEntry.place(x=1000, y=0)

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
        graphTurtle.teleport(axisDraw_y-getGraphSize()[0]*0.017, y)
        graphTurtle.goto(    axisDraw_y+getGraphSize()[0]*0.017, y)
        graphTurtle.write(y)

    # small y-axis ticks
    for y in gridSmall_y:
        graphTurtle.teleport(axisDraw_y-getGraphSize()[0]*0.007, y)
        graphTurtle.goto(    axisDraw_y+getGraphSize()[0]*0.007, y)

    # x-axis
    graphTurtle.pencolor("#FF0000")
    graphTurtle.teleport(graphBounds["llx"], axisDraw_y)
    graphTurtle.goto(    graphBounds["urx"], axisDraw_y)

    # x-axis ticks
    for x in grid_x:
        graphTurtle.teleport(x, axisDraw_x-getGraphSize()[1]*0.017)
        graphTurtle.goto(    x, axisDraw_x+getGraphSize()[1]*0.017)
        graphTurtle.write(x)

    # small x-axis ticks
    for x in gridSmall_x:
        graphTurtle.teleport(x, axisDraw_x-getGraphSize()[1]*0.007)
        graphTurtle.goto(    x, axisDraw_x+getGraphSize()[1]*0.007)

    # draw centre of graph
    if centerExistsFlag:
        graphTurtle.pencolor("#000000")
        graphTurtle.pensize(2)
        graphTurtle.teleport(axisDraw_x, axisDraw_y-getGraphSize()[0]*0.017)
        graphTurtle.goto(    axisDraw_x, axisDraw_y+getGraphSize()[0]*0.017)
        graphTurtle.teleport(axisDraw_x-getGraphSize()[0]*0.017, axisDraw_y)
        graphTurtle.goto(    axisDraw_x+getGraphSize()[0]*0.017, axisDraw_y)
        graphTurtle.pensize(1)

def drawGraph():
    """
    Draws a full graph, including the plots, points, and polygons.
    """
    graphTurtle.clear()
    drawGrid()
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
    args_joined = "".join(args)
    graphCenter_x = graphBounds["urx"]*0.5 + graphBounds["llx"]*0.5
    graphCenter_y = graphBounds["ury"]*0.5 + graphBounds["lly"]*0.5
    graphSize_x, graphSize_y = getGraphSize()

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
    
    drawGraph()


#
# RUNTIME (AND TESTING)
#

def enter_command(entry=None):
    """
    Takes commands from the entry line and sends them to the correct graph command.
    """
    command = commandEntry.get().split()[0]
    args = commandEntry.get().split()[1:]

    if command == "move": moveGraphCommand(args)
    if command == "scale": scaleGraphCommand(args)
    if command == "init": initialiseGraphCommand(args)
    if command == "exit": exitGraph()
    commandEntry.delete(0, tk.END)
window.bind("<Return>", enter_command)

drawGrid()

window.mainloop()