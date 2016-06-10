# Simulated annealing implementation
from random import random
from math import exp


def annealer(temp_f, energy_f, state_gen, accept_p, dist=random):
    def anneal(iterations=100):
        state = next(state_gen)
        for i in range(iterations):
            t = temp_f(i / iterations)
            new_state = state_gen.send(state)
            acceptance = accept_p(energy_f(state), energy_f(new_state), t)
            comp = dist()
            # print(acceptance, comp)
            if acceptance >= comp:
                state = new_state
            yield state
    return anneal


def temp_identity(t):
    return t


def basic_decrease(t):
    return 1 - t


def basic_acceptance(e1, e2, t):
    """Kirkpatrick"""
    if e2 < e1:
        return 1
    else:
        return exp(-(e2 - e1) / t)
