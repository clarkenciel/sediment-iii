import comp_math as m
import anneal as a
from random import choice, randrange as rr
from functools import partial
from math import log2


def note_to_pc(n):
    return n.written_pitch.pitch_class_number


def note_to_dur_pair(n):
    return n.written_duration.pair


def pc_gen(start, lo_lim, hi_lim):
    cur_pc = start
    clamp = partial(m.clamp, lo_lim, hi_lim)
    while True:
        val = yield cur_pc
        if val is not None:
            cur_pc = clamp(val + choice([-1, 1]))


def pc_energy(goal_pc, dist_f=m.euclid):
    def checker(pc):
        return dist_f([pc], [goal_pc])
    return checker


def note_energy(goal_note, dist_f=m.pearson):
    def checker(note):
        return dist_f(note, goal_note)
    return checker


def note_gen(start, lo_lim, hi_lim):
    cur_note = start

    def clamp(note):
        out = [m.clamp(l, h, x)
               for x, l, h in zip(note, lo_lim, hi_lim)]
        return out

    while True:
        val = yield cur_note
        if val is not None:
            p, n, d = val
            cur_note = clamp((p + choice([-1, 1]),
                              n + choice([-1, 2]),
                              d ** (log2(d) + choice([-1, 1]))))

pc_anneal = a.annealer(temp_f=lambda t: 1 - t,
                       energy_f=pc_energy(0),
                       state_gen=pc_gen(rr(-48, 48), -48, 48),
                       accept_p=a.basic_acceptance)


note_anneal = a.annealer(temp_f=lambda t: (1 - t) * 2,
                         energy_f=note_energy((0, 4, 1), m.euclid),
                         state_gen=note_gen((20, 4, 2),
                                            (-24, 1, 1),
                                            (24, 14, 8)),
                         accept_p=a.basic_acceptance)

xs = list(note_anneal(iterations=100))
print(xs[0], xs[-60:-1])
