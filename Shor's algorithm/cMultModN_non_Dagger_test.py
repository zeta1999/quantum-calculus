
from projectq.backends import CircuitDrawer
from projectq.meta import Dagger

import projectq.libs.math
import projectq.setups.decompositions
from projectq.backends import Simulator, ResourceCounter
from projectq.cengines import (AutoReplacer, DecompositionRuleSet,
                               InstructionFilter, LocalOptimizer,
                               MainEngine, TagRemover)

from projectq.ops import (All, Measure, QFT)
from homemade_code.cMultModN_non_Dagger import cMultModN_non_Dagger
from homemade_code.initialisation import initialisation, meas2int, initialisation_n
import math

def run(a=4, b=6, N = 7, x=2, param="count"):
    """
    Last update 19/02 : nb of gate linear in log(N)
    Be careful this algo is a bit long to execute
    |b> --> |b+(ax) mod N> works for
    :param a:
    :param b:
    :param N:
    :param x:
    :param param:
    :return:
    """
    # build compilation engine list
    resource_counter = ResourceCounter()
    rule_set = DecompositionRuleSet(modules=[projectq.libs.math,
                                             projectq.setups.decompositions])
    compilerengines = [AutoReplacer(rule_set),
                       TagRemover(),
                       LocalOptimizer(3),
                       AutoReplacer(rule_set),
                       TagRemover(),
                       LocalOptimizer(3),
                       resource_counter]

    # create a main compiler engine
    n = int(math.log(N, 2)) + 1

    if param == "latex":
        drawing_engine = CircuitDrawer()
        eng2 = MainEngine(drawing_engine)
        xN = initialisation_n(eng2, N, n+1)
        xx = initialisation_n(eng2, x, n+1)
        xb = initialisation_n(eng2, b, n+1)
        [xc, aux] = initialisation(eng2, [1, 0])
        cMultModN_non_Dagger(eng2, a, xb, xx, xN, aux, xc)
        eng2.flush()
        Measure | aux
        Measure | xc
        All(Measure) | xx
        All(Measure) | xb
        All(Measure) | xN
        eng2.flush()
        print(drawing_engine.get_latex())
    else:
        if param == "count":
            eng = MainEngine(resource_counter)
        else:
            eng = MainEngine(Simulator(), compilerengines)
        xN = initialisation_n(eng, N, n+1)
        xx = initialisation_n(eng, x, n+1)
        xb = initialisation_n(eng, b, n+1)
        [aux, xc] = initialisation(eng, [0, 1])
        cMultModN_non_Dagger(eng, a, xb, xx, xN, aux, xc, N)
        Measure | aux
        Measure | xc
        All(Measure) | xx
        All(Measure) | xb
        All(Measure) | xN
        eng.flush()
        if param == "count":
            return resource_counter

        measurements_b = [0]*n
        measurements_x = [0] * n
        measurements_N = [0] * n
        for k in range(n):
            measurements_b[k] = int(xb[k])
            measurements_N[k] = int(xN[k])
            measurements_x[k] = int(xx[k])

        mes_aux = int(aux[0])
        mes_c = int(aux[0])
        return [measurements_b, meas2int(measurements_b), (b+a*x) % N, measurements_N, measurements_x, mes_aux, mes_c,
                meas2int(measurements_b), meas2int(measurements_N), meas2int(measurements_x)]


L = run()
c = 0
for k in L.gate_class_counts.keys():
    c+=L.gate_class_counts[k]
print(c)
"""
import time
t1 = time.time()
L = []
#for N in range(8):
if 1:
    N=7
    print(N)
    for a in range(N):
        print(a)
        print(len(L))
        #for b in range(N):
        b =0
        if 1:
            for x in range(N):
                X = run(a, b, N, x)
                if X[1] != X[2]:
                    L.append([[a, b, N, x], X[1], X[2], X[5]])
    print(time.time()-t1)
    26.848153352737427
    25.407965421676636
    25.173583507537842
"""
