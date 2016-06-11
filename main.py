import comp_math as m
import anneal as a
import abjad as abj
import instruments
import utils as u
from abjad import scoretools as st
from copy import deepcopy
from random import choice, randrange as rr
from functools import partial


# meat of the algorithm
def pc_gen(start, lo_lim, hi_lim):
    cur_pc = start
    clamp = partial(m.clamp, lo_lim, hi_lim)
    last_add = -11
    while True:
        val = yield cur_pc
        if val is not None:
            cur_pc = clamp(val + last_add)
            last_add = int(last_add * -0.5)
            if abs(last_add) == 1:
                last_add = -11


def pc_energy(goal_pc, dist_f=m.euclid):
    def checker(pc):
        return dist_f([pc], [goal_pc])
    return checker


def collect_pcs(num_pcs, iterations, anchors, pitch_range):
    pcs = []
    tmp = []
    idx = 0
    check_len = 3
    while len(pcs) < num_pcs:
        pc_anneal = a.annealer(temp_f=lambda t: 1 - t,
                               energy_f=pc_energy(choice(anchors),
                                                  m.pitch_distance),
                               state_gen=pc_gen(choice(anchors),
                                                pitch_range[0],
                                                pitch_range[1]),
                               accept_p=a.basic_acceptance)

        for pc in pc_anneal(iterations=iterations):
            pcs.append(pc)
            if len(tmp) == check_len:
                tmp[idx] = pc
                idx = (idx + 1) % check_len
                if m.std_dev(tmp) == 0:
                    pcs = pcs[:-int(check_len/2)]
                    break
            else:
                tmp.append(pc)
    return pcs


# generate notes by repeatedly annealing
# and restarting when we reach stability
pcs = collect_pcs(60 * 4, 10,
                  [rr(-12, 12) for _ in range(5)],
                  (-24, 24))


# make notes
notes = [st.Note(pc, deepcopy(u.pc_to_dur(pc))) for pc in pcs]


# intelligently split notes
notes = u.smart_breaks(4, 16, notes)


# build parts
# TODO: figure out transpositions
insts = instruments.get_instrument_dicts(
    'Clarinet', 'Viola', 'Guitar', 'Bass')

# prep instruments
insts = instruments.prep_instruments(insts)

# pack notes
# TODO intelligent rest packing and note packing
# TODO intelligent harmonization
insts = instruments.pack_instruments(notes, insts)
# for inst in insts:
#     inst['voice'] = st.Voice(u.merge_rests(4, 16, inst['voice']))

# pack staves
staves = [instruments.make_staff((2, 4), inst) for inst in insts]

# pack score
score = st.Score(staves)

abj.show(score)
