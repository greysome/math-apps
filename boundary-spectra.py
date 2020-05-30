from tkinter import *
from common.tk_matplotlib import *
import numpy as np

canvas = root = fig = ax = None
input_coeffs = input_boundtype = input_size = var_boundtype = None

def get_coeffs():
    global input_coeffs
    coeffs = input_coeffs.get()
    # The character '|' delimits coefficients of terms with
    # negative/non-negative exponents
    neg, nonneg = coeffs.split('|')
    neg, nonneg = neg.split(','), nonneg.split(',')
    for idx, coeff in enumerate(neg):
        coeff = coeff.replace('i', 'j')
        coeff = complex(coeff)
        neg[idx] = coeff
    for idx, coeff in enumerate(nonneg):
        coeff = coeff.replace('i', 'j')
        coeff = complex(coeff)
        nonneg[idx] = coeff
    return (neg, nonneg)

def repeat_list_till(l, n):
    '''Create a new list with the elements of l repeated until n elements is reached'''
    k = n//len(l)+1
    l = l*k
    l = l[:n+1]
    return l

def toeplitz_matrix(size, coeffs, boundtype):
    M = np.zeros((size, size), dtype=np.complex64)
    neg, nonneg = coeffs

    neg.reverse()
    if boundtype == 'PBC':
        neg = repeat_list_till(neg, size)
        nonneg = repeat_list_till(nonneg, size)

    for i in range(len(neg)):
        # If terms do not fit in matrix
        if i >= len(neg):
            break
        idxs = np.arange(i+1, size)
        M[idxs, idxs-(i+1)] = neg[i]

    for i in range(len(nonneg)):
        # If terms do not fit in matrix
        if i >= len(neg)+1:
            break
        idxs = np.arange(size-i)
        M[idxs, idxs+i] = nonneg[i]

    return M

def update_view(*args):
    global ax, var_boundtype
    ax.clear()

    size = int(input_size.get())
    coeffs = get_coeffs()
    boundtype = var_boundtype.get()

    M = toeplitz_matrix(size, coeffs, boundtype)
    evs = np.linalg.eig(M)[0]
    evs = np.unique(evs)
    x, y = np.real(evs), np.imag(evs)
    ax.scatter(x, y, color='b')

    x_bound = max(abs(min(x)), abs(max(x)))
    y_bound = max(abs(min(y)), abs(max(y)))
    bound = max(x_bound, y_bound)

    ax.set_xlim(-bound, bound)
    ax.set_ylim(-bound, bound)
    centre_splines(ax)
    canvas.draw()

root = Tk()
root.title('math-apps: OBC/PBC spectra')

frame = Frame()
Label(frame, text='Coefficients').grid(row=1, column=1, sticky=W, padx=20)
input_coeffs = Entry(frame)
input_coeffs.grid(row=1, column=2, padx=20)

Label(frame, text='Boundary type').grid(row=2, column=1, sticky=W, padx=20)
var_boundtype = StringVar(frame)
var_boundtype.set('OBC')
input_boundtype = OptionMenu(frame, var_boundtype, 'OBC', 'PBC')
input_boundtype.grid(row=2, column=2, padx=20)

Label(frame, text='Matrix size').grid(row=3, column=1, sticky=W, padx=20)
input_size = Entry(frame)
input_size.grid(row=3, column=2, padx=20)

Button(frame, text='Update view', command=update_view).grid(row=4, column=1, columnspan=2, pady=10)
frame.pack()

fig = Figure(figsize=(7,7))
ax = fig.add_subplot(111)
centre_splines(ax)
canvas = draw_mpl_fig(root, fig)

Button(root, text='Quit', command=root.quit).pack()
root.mainloop()
