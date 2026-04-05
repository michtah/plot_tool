import tkinter as tk
from turtle import TurtleScreen, RawTurtle

#
# environment setup
#

# create the window for the graph.
window = tk.Tk()
window.geometry("1400x1000")

# create canvas + screen for the actual plotting
graph_canvas = tk.Canvas(width=1000, height=1000)
graph_canvas.grid(row=0,column=0)

graph_screen = TurtleScreen(graph_canvas)
graph_screen.tracer(0, 0)

# create turtle to draw graphics
t = RawTurtle(graph_screen, visible=False)

# initialise window.
window.mainloop()