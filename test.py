from cspbase import *
from cagey_csp import *
from propagators import *
from heuristics import *

import itertools
import platform
import signal
import traceback


# ================
# Timeout Handling
# ================

TIMEOUT = 60
WARNED = False

class TO_exc(Exception):
    pass

def toHandler(signum, frame):
    raise TO_exc()

def setTO(seconds):
    global WARNED
    if 'Windows' in platform.platform():
        if not WARNED:
            WARNED = True
            print("\n\n\t\tWARNING: Timeout is not available on Windows. Solving will not be capped at 60sec\n\n")
    else:
        signal.signal(signal.SIGALRM, toHandler)
        signal.alarm(seconds)



# n queens
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

# ====================
# General GAC/FC Tests
# ====================

##Tests FC after the first queen is placed in position 1.
def test_simple_FC(stu_propagators):
    score = 0

    did_fail = False
    try:
        queens = nQueens(8)
        curr_vars = queens.get_all_vars()
        curr_vars[0].assign(1)
        stu_propagators.prop_FC(queens,newVar=curr_vars[0])

        answer = [[1],[3, 4, 5, 6, 7, 8],[2, 4, 5, 6, 7, 8],[2, 3, 5, 6, 7, 8],[2, 3, 4, 6, 7, 8],[2, 3, 4, 5, 7, 8],[2, 3, 4, 5, 6, 8],[2, 3, 4, 5, 6, 7]]
        var_domain = [x.cur_domain() for x in curr_vars]

        for i in range(len(curr_vars)):
            if var_domain[i] != answer[i]:
                details = "Failed simple FC test: variable domains don't match expected results"
                did_fail = True
                break
        if not did_fail:
            score = 1
            details = ""
    except TO_exc:
        details = "Got a TIMEOUT while testing simple FC"
    except Exception:
        details = "One or more runtime errors occurred while testing simple FC: %r" % traceback.format_exc()

    return score,details

##Tests GAC after the first queen is placed in position 1.
def test_simple_GAC(stu_propagators):
    score = 0

    did_fail = False
    try:
        queens = nQueens(8)
        curr_vars = queens.get_all_vars()
        curr_vars[0].assign(1)
        stu_propagators.prop_GAC(queens,newVar=curr_vars[0])

        answer = [[1], [3, 4, 5, 6, 7, 8], [2, 4, 5, 6, 7, 8], [2, 3, 5, 6, 7, 8], [2, 3, 4, 6, 7, 8], [2, 3, 4, 5, 7, 8], [2, 3, 4, 5, 6, 8], [2, 3, 4, 5, 6, 7]]
        var_domain = [x.cur_domain() for x in curr_vars]

        for i in range(len(curr_vars)):
            if var_domain[i] != answer[i]:
                details = "Failed simple GAC test: variable domains don't match expected results."
                did_fail = True
                break
        if not did_fail:
            score = 1
            details = ""

    except Exception:
        details = "One or more runtime errors occurred while testing simple GAC: %r" % traceback.format_exc()

    return score,details





##Simple example with 3 queens that results in different pruning for FC & GAC
##Q1 is placed in slot 2, q2 is placed in slot 4, and q8 is placed in slot 8.
##Checking GAC.
def three_queen_GAC(stu_propagators):
    score = 0

    try:
        queens = nQueens(8)
        curr_vars = queens.get_all_vars()
        curr_vars[0].assign(4)
        curr_vars[2].assign(1)
        curr_vars[7].assign(5)
        stu_propagators.prop_GAC(queens)

        answer = [[4],[6, 7, 8],[1],[3, 8],[6, 7],[2, 8],[2, 3, 7, 8],[5]]
        var_vals = [x.cur_domain() for x in curr_vars]

        if var_vals != answer:
            details = "Failed three queens GAC test: variable domains don't match expected results"

        else:
            score = 1
            details = ""

    except Exception:
        details = "One or more runtime errors occurred while testing GAC with three queens: %r" % traceback.format_exc()

    return score,details


##Simple example with 3 queens that results in different pruning for FC & GAC
##Q1 is placed in slot 2, q2 is placed in slot 4, and q8 is placed in slot 8.
##Checking FC.
def three_queen_FC(stu_propagators):
    score = 0

    try:
        queens = nQueens(8)
        curr_vars = queens.get_all_vars()
        curr_vars[0].assign(4)
        curr_vars[2].assign(1)
        curr_vars[7].assign(5)
        stu_propagators.prop_FC(queens)

        answer = [[4],[6, 7, 8],[1],[3, 6, 8],[6, 7],[2, 6, 8],[2, 3, 7, 8],[5]]
        var_vals = [x.cur_domain() for x in curr_vars]

        if var_vals != answer:
            details = "Failed three queens FC test: variable domains don't match expected results"

        else:
            score = 1
            details = ""

    except TO_exc:
        details = "Got a TIMEOUT while testing three_queen_FC"
    except Exception:
        details = "One or more runtime errors occurred while testing FC with three queens: %r" % traceback.format_exc()

    return score,details


# Some simple board tests
def test_cagey_props():

    def print_cagey_soln(var_array):
        print([var.get_assigned_value() for var in var_array])

    boards = [ (3, [(3,[(1,1), (2,1)],'+'),(1, [(1,2)], '?'), (8, [(1,3), (2,3), (2,2)], "+"), (3, [(3,1)], '?'), (3, [(3,2), (3,3)], "+")]) ]
    
    score = 0
    
    for b in boards:
        print("Solving board")
        csp, var_array = cagey_csp_model(b)
        solver = BT(csp)
        print("=======================================================")
        print("FC")
        solver.bt_search(prop_FC)
        #print("GAC")
        #solver.bt_search(prop_GAC)
        print("Solution")
        print_cagey_soln(var_array)
        
        desired_cell_names = ["Cell(1,1)", f'Cell(1,{b[0]})', f'Cell({b[0]},{b[0]})']
        tested_values = [var_array[0].name, var_array[b[0]-1].name, var_array[b[0]**2-1].name]
        
        failed = False
        te, an = None, None
        for ans, test in zip(desired_cell_names, tested_values):
            if ans != test:
                failed = True
                an = ans
                te = test
                break
        if failed:
            raise Exception(f'Grid variable existence test failed: {te} does not equal {an}.')
        else:
            print(f'Grid variable existence test successful.')

        cage_names = []
        # get predicted names for all cages
        for cage in b[1]:
            # get variables involved with cages.
            in_cage = []
            for v in cage[1]:
                in_cage.append(var_array[((v[0] - 1)*b[0])+(v[1] - 1)])
            cage_names.append(f'Cage_op({cage[0]}:{cage[2]}:{in_cage})')

        # check cage name assignments
        cages = var_array[b[0]**2:]
        for cage_name in cage_names:
            found = False
            for cage in cages:
                if cage.name == cage_name:
                    found = True
                    cages.remove(cage)
                    break
            if not found:
                raise Exception(f'Cage operation variable existence test failed: found no match for {cage_name}.')
        print(f'Cage operation variable existence test successful.')

            
        
def test_mrv():

    a = Variable('A', [1])
    b = Variable('B', [1])
    c = Variable('C', [1])
    d = Variable('D', [1])
    e = Variable('E', [1])

    simpleCSP = CSP("Simple", [a,b,c,d,e])

    count = 0
    for i in range(0,len(simpleCSP.vars)):
        simpleCSP.vars[count].add_domain_values(range(0, count))
        count += 1

    var = []
    var = ord_mrv(simpleCSP)

    # print(simpleCSP.vars[0].name)
    # print(simpleCSP.vars)
    # for var in simpleCSP.vars:
    #     print(var.name)
    #     print(var.dom)

    score = 0
    details = ''

    if var:
        if((var.name) == simpleCSP.vars[0].name):
            score += 1
            details += "Passed First Ord MRV Test\n"
        else:
            details += "Failed First Ord MRV Test\n"
    else:
        print("No Variable Returned from Ord MRV")

    a = Variable('A', [1,2,3,4,5])
    b = Variable('B', [1,2,3])
    c = Variable('C', [1,2])
    d = Variable('D', [1,2,3])
    e = Variable('E', [1])

    simpleCSP = CSP("Simple", [a,b,c,d,e])

    #count = 4
    #for i in range(0,len(simpleCSP.vars)):
    #    print(simpleCSP2.vars[count].name)
    #    simpleCSP2.vars[count].add_domain_values(range(0, i))
    #    count -= 1

    var = []
    var = ord_mrv(simpleCSP)

    # print("{}".format(simpleCSP.vars[len(simpleCSP.vars)-1].name))
    # print(simpleCSP.vars)
    # for var in simpleCSP.vars:
    #     print(var.name)
    #     print(var.dom)

    if var:
        if((var.name) == simpleCSP.vars[len(simpleCSP.vars)-1].name):
            score += 1
            details += "Passed Second Ord MRV Test"
        else:
            details += "Failed Second Ord MRV Test"
    else:
        print("No Variable Returned from Ord MRV")

    return score, details

# Run Tests
def main(stu_propagators=None):
    tests = 7
    total_score = 0

    if stu_propagators == None:
        import propagators as stu_propagators

    # begin timer
    try:
        setTO(TIMEOUT)
        #begin tests
        print("---starting test_simple_FC---")
        score,details = test_simple_FC(stu_propagators)
        total_score += score
        print(details)
        print("---finished test_simple_FC---\n")

        print("---starting test_simple_GAC---")
        score,details = test_simple_GAC(stu_propagators)
        total_score += score
        print(details)
        print("---finished test_simple_GAC---\n")

        print("---starting three_queen_FC---")
        score,details = three_queen_FC(stu_propagators)
        total_score += score
        print(details)
        print("---finished three_queen_FC---\n")

        print("---starting three_queen_GAC---")
        score,details = three_queen_GAC(stu_propagators)
        total_score += score
        print(details)
        print("---finished three_queen_GAC---\n")

        try:
            print("---start test_cagey_props---")
            test_cagey_props()
            total_score += 1
            print("---finished test_cagey_props---\n")
        except Exception as e:
            print("---test_cagey_props failed---\n")
            # print the error and stack trace
            print(e)
            print(traceback.format_exc())

        try:
            print("---starting test_mrv---")
            score,details = test_mrv() # 2 tests
            total_score += score
            print(details)
            print("---finished test_mrv---\n")
        except Exception as e:
            print("---test_mrv failed---\n")
            # print the error and stack trace
            print(e)
            print(traceback.format_exc())

        setTO(0)

    except TO_exc:
        print(f'\n\n\nATTENTION!!!!\nSystem timed out!')
    except Exception:
        print(f'Something went wrong: {traceback.format_exc()}')

    # end testing
    setTO(0)
    print(f'\tTotal score {total_score}/{tests}\n')

if __name__=="__main__":
    main()
    