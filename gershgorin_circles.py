from tkinter import *
from common.tk_matrix import TkMatrix
from common.tk_matplotlib import *
import numpy as np

canvas = root = fig = ax = None

def update(value):
    global ax
    ax.clear()

    # 1. Plot eigenvalues
    evs = np.linalg.eig(value)[0]
    evs = np.unique(evs)
    ax.scatter(np.real(evs), np.imag(evs), color='b')

    # 2. Draw gershgorin circles
    rows, cols = value.shape
    x = []
    y = []
    for i in range(rows):
        # Diagonal entry in row
        centre = (np.real(value[i][i]), np.imag(value[i][i]))
        # Sum of absolute values of non-diagonal entries in row
        radius = sum(abs(value[i][j]) for j in range(cols) if i != j)
        x.extend([centre[0]-radius, centre[0]+radius])
        y.extend([centre[1]-radius, centre[1]+radius])
        circle = plt.Circle(centre, radius, color='black', fill=False)
        ax.add_artist(circle)

    # Ensure gershgorin circles fit in plot
    offset_x = 0.1*(max(x)-min(x))
    offset_y = 0.1*(max(y)-min(y))
    if offset_x == 0:
        offset_x = 1
    if offset_y == 0:
        offset_y = 1

    x_low = min(x) - offset_x
    x_high = max(x) + offset_x
    y_low = min(y) - offset_y
    y_high = max(y) + offset_y

    # Ensure origin is at the center
    x_max_abs = max(abs(x_low), abs(x_high))
    y_max_abs = max(abs(y_low), abs(y_high))
    x_low, x_high = -x_max_abs, x_max_abs
    y_low, y_high = -y_max_abs, y_max_abs

    # Modify axes so that gershgorin circles appear round
    x_range = x_high - x_low
    y_range = y_high - y_low
    a = max(x_range, y_range)
    if a == x_range:
        y_low -= (x_range - y_range) / 2
        y_high += (x_range - y_range) / 2
    elif a == y_range:
        x_low -= (y_range - x_range) / 2
        x_high += (y_range - x_range) / 2

    ax.set_xlim(x_low, x_high)
    ax.set_ylim(y_low, y_high)
    centre_splines(ax)
    canvas.draw()

root = Tk()
root.title('math-apps: Greshgorin Circles')
TkMatrix(
    root, command=update,
    assertions=[(lambda value: value.shape[0] == value.shape[1], 'non-square matrix')]
).pack()

fig = Figure(figsize=(5,5))
ax = fig.add_subplot(111)
ax.autoscale(tight=True)
centre_splines(ax)
canvas = draw_mpl_fig(root, fig)

Button(root, text='Quit', command=root.quit).pack()
root.mainloop()
