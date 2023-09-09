import numpy as np
import pandas as pd
from cvxpy import *
from portfolio.trash.data_functions import *

mp = data.loading(["cdr", "tim", "pko"]).set_index("Month")
mr = pd.DataFrame()


# compute monthly returns

for s in mp.columns:
    date = mp.index[0]
    pr0 = mp[s][date] 
    for t in range(1,len(mp.index)):
        date = mp.index[t]
        pr1 = mp[s][date]
        ret = (pr1-pr0)/pr0
        mr._set_value(date,s,ret)
        pr0 = pr1


r = np.asarray(np.mean(mr, axis=0))
C = np.asmatrix(np.cov(mr, rowvar=False))


# Get symbols
symbols = mr.columns

# Number of variables
n = len(symbols)

# The variables vector
x = Variable(n)

# The minimum return
req_return = 0.02

# The return
ret = r.T@x

# The risk in xT.Q.x format
risk = quad_form(x, C)

# The core problem definition with the Problem class from CVXPY
prob = Problem(Minimize(risk), [sum(x)==1, ret >= req_return, x >= 0])


try:
    prob.solve()
    print ("Optimal portfolio")
    print ("----------------------")
    for s in range(len(symbols)):
       print (" Investment in {} : {}% of the portfolio".format(symbols[s],round(100*x.value[s],2)))
    print ("----------------------")
    print ("Exp ret = {}%".format(round(100*ret.value,2)))
    print ("Expected risk    = {}%".format(round(100*risk.value**0.5,2)))
except:
    print ("Error")