
# CISC 352
# csp_sample_run.py
# desc: provides a sample csp implementation of a simple math problem, the colouring of the australian graph, and
#       the n-queens problem.
#

from cspbase import *
from propagators import *
import itertools


# ==============
# Simple Example
# ==============
"""
 Here is a simple and easy to follow Constraint Satisfaction Problem
 There are four variables: w, x, y, z
 w can be any natural number [1-4]
 x, y, z can be any natural number [1-3]

 this problem is structured as such:
 We must find valuations for all variables such that

 W = X + Y + Z
 AND
 X = Y + Z
"""

x = Variable('X', [1, 2, 3])
y = Variable('Y', [1, 2, 3])
z = Variable('Z', [1, 2, 3])
w = Variable('W', [1, 2, 3, 4])

def w_eq_sum_x_y_z(wxyz):
    """
    takes a list of valuations and attempts to determine if this is a valid assignment
    :param wxyz:
    :return:
    """
    # note inputs lists of value
    w = wxyz[0]
    x = wxyz[1]
    y = wxyz[2]
    z = wxyz[3]
    return w == x + y + z


c1 = Constraint('C1', [x, y, z])
# c1 is constraint x == y + z. Below are all of the satisfying tuples
c1.add_satisfying_tuples([[2, 1, 1], [3, 1, 2], [3, 2, 1]])

c2 = Constraint('C2', [w, x, y, z])
# c2 is constraint w == x + y + z. Instead of writing down the satisfying
# tuples we compute them

varDoms = []
for v in [w, x, y, z]:
    varDoms.append(v.domain())

sat_tuples = []
for t in itertools.product(*varDoms):
    # NOTICE use of * to convert the list v to a sequence of arguments to product
    if w_eq_sum_x_y_z(t):
        sat_tuples.append(t)

c2.add_satisfying_tuples(sat_tuples)

simpleCSP = CSP("SimpleEqs", [x,y,z,w])
simpleCSP.add_constraint(c1)
simpleCSP.add_constraint(c2)

btracker = BT(simpleCSP)
# btracker.trace_on()

print("Plain Bactracking on simple CSP")
btracker.bt_search(prop_BT)
print("=======================================================")
# print("Forward Checking on simple CSP")
# btracker.bt_search(prop_FC)
# print("=======================================================")
# print("GAC on simple CSP")
# btracker.bt_search(prop_GAC)


# ======================
# graph painting problem
# ======================
"""
Australia is roughly divided into states/territories like so:
       __  |\
   ,'`/  (,| \
 ,'   |NT | QL \
( WA  |----|____\
 \   ,|_,SA|NSW./
  (_/    `^|`~,/
           `-^'     <- V
             __
             \/     <- T

If we view it as a graph it looks something like this:
   (NT) -- (QL)
  /  |   /   |
(WA) |  /    |
  \  | /     |
   (SA) -- (NSW)
      \      |
       \___ (V)
             |
            (T)

Our task here is to paint each region one of the colours:
- Red
- Green
- Blue
Such that no two adjacent territories are painted the same colour.
"""


def neighbors_not_equal(dom):
    """
    takes a domain of colours and generates all satisfying tuples where the neighboring cells are not equal
    :param dom: a domain of colours e.g. R,G,B
    :return: a list of satifying colourations e.g. [("G", "B"), ("R", "G"), ...]
    """
    return [[o, x] for (o, x) in itertools.product(dom, repeat=2) if o != x]

def add_edge(v_name1, v_name2, vert, sat_tuple):
    """
    takes two names for the vertices, a list referencing said vertices, and a list of satisfying colouration tuples
    to generate a corresponding pair of bidirectional constraint objects (stored in list)
    :param v_name1: name of the first vertex
    :param v_name2: name of the second vertex
    :param vert: array of the two vertices
    :param sat_tuple: list of satisfying tuples
    :return: returns a list containing the two constraints on a single edge. (V1, V2) & (V2, V1)
    """
    con1 = Constraint(f'C({v_name1}, {v_name2})', [vert[0], vert[1]])
    con2 = Constraint(f'C({v_name2}, {v_name1})', [vert[1], vert[0]])
    con1.add_satisfying_tuples(sat_tuple)
    con2.add_satisfying_tuples(sat_tuple)
    return [con1, con2]


def australiaPaint():
    """
    generates a standard CSP which contains a graph of australia to be coloured
    :return: a csp object encapsulating this problem.
    """
    # define all variables/their domains
    dom = ['R', 'G', 'B']  # red, green, blue respectively

    wa = Variable("Western Australia", dom)
    nt = Variable("Northern Territory", dom)
    ql = Variable("Queensland", dom)
    sa = Variable("South Australia", dom)
    nsw = Variable("New South Wales", dom)
    v = Variable("Victoria", dom)
    t = Variable("Tasmania", dom)

    # populate our constraints
    cons = []
    sat_tuple = neighbors_not_equal(dom)

    # define constraint on the Tasmanian Vertex
    cons += add_edge("T", "V", [t, v], sat_tuple)

    # define constraint on the Victoria Vertex
    cons += add_edge("V", "SA", [v, sa], sat_tuple)
    cons += add_edge("V", "NSW", [v, nsw], sat_tuple)

    # define constraint on the New South Wales Vertex
    cons += add_edge("NSW", "QL", [nsw, ql], sat_tuple)
    cons += add_edge("NSW", "SA", [nsw, sa], sat_tuple)

    # define constraint on the Queensland Vertex
    cons += add_edge("QL", "NT", [ql, nt], sat_tuple)
    cons += add_edge("QL", "SA", [ql, sa], sat_tuple)

    # define constraint on the Northern Territory Vertex
    cons += add_edge("NT", "SA", [nt, sa], sat_tuple)
    cons += add_edge("NT", "WA", [nt, wa], sat_tuple)

    # define constraint on the Western Australian Vertex
    cons += add_edge("WA", "SA", [wa, sa], sat_tuple)

    # define constrains on the South Australia Vertex
    # implicitly created through all other vertex definitions

    # define problem structure
    csp = CSP("Colour Australia", [wa, nt, ql, sa, nsw, v, t])
    for c in cons:
        csp.add_constraint(c)
        # print(cons)
    return csp


def solve_graph_color(propType, trace=False):
    """
    use the format of our standard constraint solver to solve the australia painting problem.
    :param propType: defines which propagation algorithm we want to use
    :param trace: whether or not a trace algorithm wants to be employed
    """
    csp = australiaPaint()
    solver = BT(csp)
    if trace:
        solver.trace_on()
    if propType == 'BT':
        solver.bt_search(prop_BT)
    elif propType == 'FC':
        solver.bt_search(prop_FC)
    elif propType == 'GAC':
        solver.bt_search(prop_GAC)

# ===============
# Execution block
# ===============
trace = False
print("Plain Backtracking on Colouring Australia")
solve_graph_color('BT', trace)
print("=========================================")
# trace = False
# print("Forward Checking on Colouring Australia")
# solve_graph_color('FC', trace)
# print("=========================================")


# ================
# n-queens problem
# ================
"""
Queens are the single most mobile piece in the game of chess. Because of this, arranging N queens on a board of size
NxN can be quite challenging.
There exists a valid arrangement of N queens for all N >= 4.
"""

def queensCheck(qi, qj, i, j):
    '''Return true if i and j can be assigned to the queen in row qi and row qj
       respectively. Used to find satisfying tuples.
    '''
    return i != j and abs(i-j) != abs(qi-qj)

def nQueens(n):
    '''Return an n-queens CSP'''
    i = 0
    dom = []
    for i in range(n):
        dom.append(i+1)

    vars = []
    for i in dom:
        vars.append(Variable('Q{}'.format(i), dom))

    cons = []
    for qi in range(len(dom)):
        for qj in range(qi+1, len(dom)):
            con = Constraint("C(Q{},Q{})".format(qi+1,qj+1),[vars[qi], vars[qj]])
            sat_tuples = []
            for t in itertools.product(dom, dom):
                if queensCheck(qi, qj, t[0], t[1]):
                    sat_tuples.append(t)
            con.add_satisfying_tuples(sat_tuples)
            cons.append(con)

    csp = CSP("{}-Queens".format(n), vars)
    for c in cons:
        csp.add_constraint(c)
    return csp

def solve_nQueens(n, propType, trace=False):
    csp = nQueens(n)
    solver = BT(csp)
    if trace:
        solver.trace_on()
    if propType == 'BT':
        solver.bt_search(prop_BT)
    elif propType == 'FC':
        solver.bt_search(prop_FC)
    elif propType == 'GAC':
        solver.bt_search(prop_GAC)

trace = False
#trace = False
print("Plain Bactracking on 8-queens")
solve_nQueens(16, 'BT', trace)
print("=======================================================")
#print("Forward Checking 8-queens")
#solve_nQueens(8, 'FC', trace)
#print("=======================================================")
#print("GAC 8-queens")
#solve_nQueens(8, 'GAC', trace)

