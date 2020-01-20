from tkinter import *
from common.tk_matrix import TkMatrix
from common.tk_matplotlib import *
from common.tk_scrollable_frame import ScrollableFrame
import numpy as np

root = scrollbar = steps_view = None
step_widgets = []

def add_step(row, description, value):
    global steps_view, step_widgets
    font = Label()
    label = Label(steps_view.frame, text=description, font='arial 10 bold')
    matrix = TkMatrix(steps_view.frame, value=value, editable=False)
    label.grid(row=row, column=0, pady=10, padx=5, sticky=W)
    matrix.grid(row=row, column=1, pady=10, padx=5)
    step_widgets.extend([label, matrix])

def get_leading_idx(row):
    '''
    Return index of first nonzero entry of row, or -1 if there are none.
    '''
    try:
        return np.where(row != 0)[0][0]
    except IndexError:
        return -1

def update(value):
    global steps_view, step_widgets
    row = 0
    n_rows, n_cols = value.shape

    for i in step_widgets:
        i.destroy()
    step_widgets = []

    # Swap rows so that rows with nonzero first entry come first
    for i in range(n_rows):
        if value[i][0] == 0:
            # Find the first row from the back with nonzero first
            # entry to swap with
            for j in range(n_rows-1, i, -1):
                if value[j][0] != 0:
                    # Swap rows
                    value[[i, j]] = value[[j, i]]
                    add_step(row, f'R{i+1} ↔ R{j+1}', value)
                    row += 1
                    break

    # Transform to upper triangular matrix
    for subtrahend in range(n_rows):
        for minuend in range(subtrahend+1, n_rows):
            # Happen when there are more rows than columns, in which case
            # the extra rows would have been zeroed out
            if subtrahend >= n_cols:
                break

            # There is a zero entry on the main diagonal, matrix
            # cannot be row reduced
            if value[subtrahend][subtrahend] == 0:
                break

            # Subtract each row such that the entry on the main diagonal is the
            # first nonzero entry
            scale_factor = value[minuend][subtrahend] / value[subtrahend][subtrahend]
            value[minuend] -= scale_factor * value[subtrahend]

            add_step(row, f'R{minuend+1} ← R{minuend+1} - {scale_factor} * R{subtrahend+1}', value)
            row += 1

    # Scale all rows such that leading value is 1
    for i in range(n_rows):
        leading_idx = get_leading_idx(value[i])
        if leading_idx != -1:
            scale_factor = value[i][leading_idx]
            if scale_factor != 1:
                value[i] /= scale_factor
                add_step(row, f'R{i+1} ← R{i+1} / {scale_factor}', value)
                row += 1

    # Subtract away trailing row entries
    for minuend in range(n_rows-2, -1, -1):
        for subtrahend in range(minuend+1, n_rows):
            # Happen when there are more rows than columns, in which case
            # the extra rows would have been zeroed out
            if subtrahend >= n_cols:
                break

            # There is a zero entry on the main diagonal, matrix
            # cannot be row reduced
            if value[subtrahend][subtrahend] == 0:
                break

            # Subtract each row such that the entry on the main diagonal is the
            # Matrix cannot be reduced to reduced row echoleon form
            if value[subtrahend][subtrahend] == 0:
                break

            # Subtract away as many entries of the row following the entry on the main diagonal
            scale_factor = value[minuend][subtrahend] / value[subtrahend][subtrahend]
            value[minuend] -= scale_factor * value[subtrahend]

            add_step(row, f'R{minuend+1} ← R{minuend+1} - {scale_factor} * R{subtrahend+1}', value)
            row += 1

root = Tk()
root.title('math-apps: Gaussian Elimination')
TkMatrix(root, command=update).pack()

steps_view = ScrollableFrame(root)
steps_view.pack(pady=10)

Button(root, text='Quit', command=root.quit).pack()
root.mainloop()
