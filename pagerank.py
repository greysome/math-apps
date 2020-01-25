from tkinter import *
from common.tk_matrix import TkMatrix
from common.tk_matplotlib import *
from matplotlib import cm
from matplotlib.ticker import MaxNLocator
import numpy as np
import networkx as nx

ax_graph = input_m = None
input_matrix = None

def all_integers(value):
    value = value.flatten()
    for i in range(len(value)):
        if int(value[i]) != value[i]:
            return False
    return True

def ge_one(value):
    value = value.flatten()
    return len(np.where(value >= 1)[0]) == len(value)

def no_node_gaps(value):
    value = value.flatten()
    for i in range(1, int(np.amax(value))):
        if len(np.where(value == i)[0]) == 0:
            return False
    return True

def no_self_links(value):
    for i in range(value.shape[0]):
        a, b = value[i][0], value[i][1]
        if a == b:
            return False
    return True

def build_link_matrix(edges):
    n = np.amax(edges)
    A = np.zeros((n,n))

    # Keep track of links for each node
    L = dict()
    for i in range(1, n+1):
        L[i] = []
    for e in edges:
        L[e[0]].append(e[1])

    # Populate link matrix
    for k, v in L.items():
        for i in v:
            if len(v) != 0:
                A[i-1][k-1] = 1 / len(v)

    return A

def modify_link_matrix(A, m):
    n = A.shape[0]
    S = np.full((n, n), 1/n)
    return (1-m)*A + m*S

def update_input_matrix(value):
    global input_matrix
    # Prevent any errors resulting from working with float-typed integers (like 5.0)
    input_matrix = value.astype('int64')

def get_m():
    global input_m
    try:
        m = float(input_m.get())
    except ValueError:
        m = 0.15
    else:
        if m <= 0:
            m = 0.01
        elif m > 1:
            m = 1

    input_m.delete(0, END)
    input_m.insert(0, str(m))
    return m

def update_graph():
    edges = []
    for i in range(input_matrix.shape[0]):
        edges.append((input_matrix[i][0], input_matrix[i][1]))

    A = build_link_matrix(edges)
    n = A.shape[0]
    M = modify_link_matrix(A, get_m())
    # The typical use-case will not involve that many nodes, hence
    # compute importance scores the direct way over power iteration
    lambdas, vs = np.linalg.eig(M)
    # Get only real eigenvalues
    real_idxs = np.where(np.imag(lambdas) == 0)[0]
    lambdas = lambdas[real_idxs]
    vs = vs[:,real_idxs]
    max_idx = np.argmax(np.abs(lambdas))

    importance_scores = vs[:,max_idx]
    # Normalise such that the maximum entry is 1
    importance_scores /= sum(importance_scores)
    importance_scores = importance_scores.astype('float64')

    # Update graph
    node_size = np.full(n, 400, dtype='float64')
    # Nodes with larger importance scores appear bigger and darker
    node_size += 2000 * importance_scores
    score_min, score_max = np.amin(importance_scores), np.amax(importance_scores)
    colormap = cm.get_cmap('Wistia')
    node_color = [colormap(0.2 + importance_scores[i] * 0.6) for i in range(n)]

    G = nx.DiGraph(edges)
    pos = nx.circular_layout(G)
    ax_graph.clear()
    nx.draw_networkx(G, pos=pos, ax=ax_graph, node_size=node_size, node_color=node_color,
                     nodelist=range(1, n+1), font_weight='bold')
    ax_graph.set_axis_off()

    # Update histogram of importance scores
    order = np.flip(np.argsort(importance_scores))
    importance_scores = importance_scores[order]
    ax_scores.clear()
    ax_scores.bar(np.arange(1, n+1), importance_scores, width=0.5)
    # x ticks include that at x=0
    ax_scores.set_xticklabels([''] + list(order + 1))
    # Set ticks only at integers
    ax_scores.xaxis.set_major_locator(MaxNLocator(integer=True))

    ax_graph.set_title('Link Graph')
    ax_scores.set_title('Importance Scores')
    canvas.draw()

root = Tk()
root.title('math-apps: PageRank')

frame = Frame(root)

Label(frame, text='Edges list').grid(row=1, column=1, sticky=W, padx=20)
TkMatrix(
    frame, command=update_input_matrix,
    assertions=[(lambda value: value.shape[1] == 2, 'no. of columns must be exactly 2'),
                (all_integers, 'each entry must be an integer'),
                (ge_one, 'each entry must be >= 1'),
                (no_node_gaps, 'all integers between 1 and max must be taken on'),
                (no_self_links, 'no self links allowed')]
).grid(row=1, column=2)

Label(frame, text='m').grid(row=2, column=1, sticky=W, padx=20)
input_m = Entry(frame)
input_m.grid(row=2, column=2)

Button(frame, text='Update Graph', command=update_graph).grid(row=3, column=1, columnspan=2, pady=10)

frame.pack()

fig = Figure(figsize=(10,5))
ax_graph = fig.add_subplot(121)
ax_scores = fig.add_subplot(122)
ax_graph.set_axis_off()
ax_graph.set_title('Link Graph')
ax_scores.set_title('Importance Scores')
centre_splines(ax_graph)
canvas = draw_mpl_fig(root, fig)

Button(root, text='Quit', command=root.quit).pack()
root.mainloop()
