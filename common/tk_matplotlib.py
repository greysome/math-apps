'''
Convenience methods for integrating matplotlib plots into Tkinter.
'''

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from math import ceil, floor

def centre_splines(ax):
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

def draw_mpl_fig(parent, fig):
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    toolbar = NavigationToolbar2Tk(canvas, parent)
    toolbar.update()
    canvas.get_tk_widget().pack()
    return canvas

def get_centering_bounds(x, y):
    offset_x = 0.1*(max(x)-min(x))
    offset_y = 0.1*(max(y)-min(y))
    if offset_x == 0:
        offset_x = 1
    if offset_y == 0:
        offset_y = 1

    x_low = floor(min(x) - offset_x)
    x_high = ceil(max(x) + offset_x)
    y_low = floor(min(y) - offset_y)
    y_high = ceil(max(y) + offset_y)

    # Ensure origin is at the center
    x_max_abs = max(abs(x_low), abs(x_high))
    y_max_abs = max(abs(y_low), abs(y_high))
    x_low, x_high = -x_max_abs, x_max_abs
    y_low, y_high = -y_max_abs, y_max_abs
    return x_low, x_high, y_low, y_high
