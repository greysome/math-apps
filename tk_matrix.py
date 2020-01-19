'''
Implementation of a Tkinter widget for inputting matrices.
'''

from tkinter import *
import numpy as np

class TkEditMatrixDialog(object):
    DEFAULT_SEP = ','

    def __init__(self, parent, value):
        top = self.top = Toplevel(parent)

        self.value = value

        self.error = Label(top, text='')
        self.error.grid(row=0, columnspan=2)

        self.input_matrix = Text(top, width=50, height=25)
        self.input_matrix.grid(row=1, columnspan=2)
        rows, cols = value.shape
        for i in range(rows):
            for j in range(cols):
                self.input_matrix.insert(END, '%g' % value[i][j])
                if j < cols-1:
                    self.input_matrix.insert(END, ',')
            self.input_matrix.insert(END, '\n')

        self.input_matrix.tag_add(SEL, 1.0, END)
        self.input_matrix.bind('<Control-Return>', self.done)
        self.input_matrix.focus_set()

        Label(top, text='Separator').grid(row=2, padx=5, pady=5)
        var_sep = StringVar()
        self.input_sep = Entry(top, textvariable=var_sep)
        self.input_sep.insert(0, TkEditMatrixDialog.DEFAULT_SEP)
        self.input_sep.grid(row=2, column=1, pady=5)
        var_sep.trace('w', self.max_one_char)

        Button(top, text='Ok', command=self.done).grid(row=3, columnspan=2)
        parent.wait_window(top)

    def max_one_char(self, *args):
        sep = self.input_sep.get()
        if len(sep) > 1:
            self.input_sep.delete(0, END)
            self.input_sep.insert(0, sep[0])

    def done(self, *args):
        sep = self.input_sep.get()
        if sep == '':
            sep = ' '

        raw = self.input_matrix.get(1.0, END)
        raw = raw.lstrip('\n').rstrip('\n')

        if raw == '':
            self.error['text'] = 'ERROR: empty matrix'
            return

        raw_rows = raw.split('\n')
        matrix = [raw_row.split(sep) for raw_row in raw_rows]
        try:
            matrix = [[float(i) for i in row] for row in matrix]
        except ValueError:
            self.error['text'] = 'ERROR: some entries are not numbers'
            return

        row_lens = [len(row) for row in matrix]
        if row_lens.count(row_lens[0]) != len(row_lens):
            self.error['text'] = 'ERROR: irregular dimensions'
            return

        try:
            self.value = np.array(matrix)
        except:
            self.error['text'] = 'ERROR: could not convert to numpy array'
            return

        self.top.destroy()

class TkMatrix(Frame):
    def __init__(self, parent, value=None, command=None, editable=True):
        Frame.__init__(self, parent)
        self.command = command

        if value is None:
            self.rows = self.cols = 3
            self.value = np.zeros((self.rows, self.cols))
        else:
            self.rows, self.cols = value.shape
            self.value = value

        # Holds the existing labels in matrix view, to be destroyed
        # and replaced when the matrix is updated.
        self.tmp_labels = []

        if editable:
            Button(self, text='Edit', command=self.edit_matrix).pack()

        self.matrix_view = Frame(self)
        self.matrix_view.pack()
        self.update_matrix_view()

    def update_matrix_view(self):
        for i in range(self.rows):
            for j in range(self.cols):
                # '%g' for pretty-printing
                label = Label(self.matrix_view, text='%g' % self.value[i][j])
                label.grid(row=i, column=j)
                self.tmp_labels.append(label)

    def edit_matrix(self):
        dialog = TkEditMatrixDialog(self, self.value)
        self.value = dialog.value
        self.rows, self.cols = self.value.shape

        for i in self.tmp_labels:
            i.destroy()
        self.tmp_labels = []
        self.update_matrix_view()

        if self.command != None:
            self.command(self.value)
