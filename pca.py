from tkinter import *
from common.tk_matrix import TkMatrix
from common.tk_matplotlib import *
from matplotlib.ticker import MaxNLocator
import numpy as np

root = canvas = ax_output = ax_pcs = input_axis1 = input_axis2 = None
n = X_raw = None

def update_input_view(*args):
    global n, X_raw
    ax_input.clear()

    if not n or X_raw is None:
        return

    try:
        axis1, axis2 = int(input_axis1.get()), int(input_axis2.get())
    except ValueError:
        pass
    else:
        if 1 <= axis1 <= n and 1 <= axis2 <= n:
            xs, ys = X_raw[[axis1-1, axis2-1]]
            x_low, x_high, y_low, y_high = get_centering_bounds(xs, ys)
            ax_input.scatter(xs, ys, color='b')
            ax_input.set_xlim(x_low, x_high)
            ax_input.set_ylim(y_low, y_high)
            centre_splines(ax_input)
            ax_input.set_title('Input (2 axes)')
            canvas.draw()

def pca(value):
    global n, X_raw
    X_raw = value
    n = X_raw.shape[1]

    input_axis1.config(from_=1, to=n, textvariable=IntVar(value=1))
    input_axis2.config(from_=1, to=n, textvariable=IntVar(value=2))
    update_input_view()

    ax_output.clear()
    ax_variances.clear()

    # Center the data points of X at the origin
    X = X_raw - np.reshape(np.mean(X_raw, axis=1), (-1, 1))

    cov_X = np.dot(X, X.transpose()) / n
    lambdas, Pt = np.linalg.eig(cov_X)
    P = Pt.transpose()

    # Arrange by descending order of eigenvalues
    order = np.flip(np.argsort(lambdas))
    P = P[order]
    lambdas = lambdas[order]

    # Keep only first 2 dimensions for plotting
    Y = np.dot(P, X)
    xs, ys = Y[0], Y[1]
    x_low, x_high, y_low, y_high = get_centering_bounds(xs, ys)

    ax_output.scatter(xs, ys, color='b')
    ax_output.set_xlim(x_low, x_high)
    ax_output.set_ylim(y_low, y_high)
    centre_splines(ax_output)

    ax_variances.bar(np.arange(1, len(lambdas)+1), lambdas, width=0.5)
    # Set ticks only at integers
    ax_variances.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax_output.set_title('Output (2 largest components)')
    ax_variances.set_title('Variances')

    canvas.draw()

root = Tk()
root.title('math-apps: PCA')

frame = Frame()
Label(frame, text='Input matrix').grid(row=1, column=1, sticky=W, padx=20)
TkMatrix(
    frame, command=pca,
    assertions=[(lambda value: value.shape[0] >= 2, '>= 2 rows required')]
).grid(row=1, column=2)

Label(frame, text='Axis 1').grid(row=2, column=1, sticky=W, padx=20)
input_axis1 = Spinbox(frame, from_=0, to=0)
input_axis1.grid(row=2, column=2)

Label(frame, text='Axis 2').grid(row=3, column=1, sticky=W, padx=20)
input_axis2 = Spinbox(frame, from_=0, to=0)
input_axis2.grid(row=3, column=2)

Button(frame, text='Update input view', command=update_input_view).grid(row=4, column=1, columnspan=2, pady=10)
frame.pack()

fig = Figure(figsize=(15,5))
ax_input = fig.add_subplot(131)
ax_output = fig.add_subplot(132)
ax_variances = fig.add_subplot(133)
ax_input.set_title('Input (2 axes)')
ax_output.set_title('Output (2 largest components)')
ax_variances.set_title('Variances')
centre_splines(ax_output)
canvas = draw_mpl_fig(root, fig)

Button(root, text='Quit', command=root.quit).pack()
root.mainloop()
