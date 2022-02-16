# =============================
# Student Names: E Ching Kho (Noon) (20118077) (17eck3@queensu.ca) & Chenhao Zhu (20112538) (17cz43@queensu.ca) & Sifan Zhu(20091314) (17sz36@queensu.ca)
# Group ID: 58 
# Date: Feb.15.2022
# =============================
# CISC 352 - W22
# heuristics.py
# desc:
#


#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.

'''This file will contain different constraint propagators to be used within
   the propagators

var_ordering == a function with the following template
    var_ordering(csp)
        ==> returns Variable

    csp is a CSP object---the heuristic can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    var_ordering returns the next Variable to be assigned, as per the definition
    of the heuristic it implements.
'''

def ord_dh(csp):
    ''' return variables according to the Degree Heuristic '''
    
    variable_name = []
    temp = []

    for i in csp.get_all_vars():
        variable_name.append(i) # add all names into the list for later output
        elem = len(csp.get_cons_with_var(i))
        temp.append(elem)
    position = temp.index(max(temp)) #drgree huristic obtain the max num
    return variable_name[position]




def ord_mrv(csp):

    ''' return variable according to the Minimum Remaining Values heuristic '''
    
    '''
    num_v = []
    var_store = []
    for element in csp.get_all_vars():
        var_store.append(element)
    '''
    variable_name = []
    position = []
    for i in csp.get_all_vars():
        variable_name.append(i) #add all names into the list
        position.append(i.domain())
    temp = []
    for elem in position:
        temp.append(len(elem)) #record the num of the cons
        item_to_add = min(temp)
        index = temp.index(item_to_add)
    return variable_name[index] #return the value with the index








