import math
from projectq.ops import X
from numpy import argmax


def int2bit(a):
    if a == 0:
        na = 1
    else:
        n_float = math.log(a, 2)
        na = math.ceil(n_float)
        if math.ceil(n_float) == n_float:
            na += 1
    La = [int(x) for x in bin(a)[2:]]
    La.reverse()
    return [La, na]


def meas2int(L: list):
    L.reverse()
    res = ''
    for i in range(len(L)):
        res += str(L[i])
    L.reverse()
    return int(res, 2)


def initialisation_n(eng, a, n):
    [L, na] = int2bit(a)
    eps = n-na
    for i in range(eps):
        L.append(0)

    # cas ou a > 2**n le dernier bit n'est pas à zéro
    """
    if L[-1] != 0 and eps <= 0:
        print(a,n, L[-1])
        L[-1] = 0
    """

    xa = eng.allocate_qureg(n)
    for i in range(n):
        if L[i]:
            X | xa[i]
    return xa


def initialisation(eng, args):
    # TODO add flexibility to the inputs here only a list of int is accepted with *args
    # Be carefull it returns a fixed length qubits so generate don't ancilla with other qubits

    # Initialisation
    m = len(args)
    L = []
    N = []
    Xreg = []
    for i in range(m):
        [Lx, nx] = int2bit(args[i])
        L.append(Lx)
        N.append(nx)
    narg = argmax(N)
    n = N[narg]
    for i in range(m):
        eps = n-N[i]
        for _ in range(eps):
            L[i].append(0)
    for _ in range(m):
        Xreg.append(eng.allocate_qureg(n))

    # initialisation de a, b et N
    for j in range(m):
        for i in range(n):
            if L[j][i]:
                X | Xreg[j][i]

    return Xreg


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def mod_inv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m