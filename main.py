import comp_math as m
import anneal as a
import abjad as abj
from collections import OrderedDict
from abjad import scoretools as st
from abjad.tools import pitchtools as pt
from copy import deepcopy
from random import choice, random, randrange as rr
from functools import partial
from math import log2


# helpers
def note_to_pc(n):
    return n.written_pitch.pitch_class_number


def note_to_dur_pair(n):
    return n.written_duration.pair


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


# generate notes by repeatedly annealing
# and restarting when we reach stability
pcs = []
tmp = []
anchors = [rr(-24, 24) for _ in range(5)]
idx = 0
check_len = 3
while len(pcs) < 60 * 4 * 4:
    pc_anneal = a.annealer(temp_f=lambda t: 1 - t,
                           energy_f=pc_energy(choice(anchors),
                                              m.pitch_distance),
                           state_gen=pc_gen(choice(anchors), -24, 24),
                           accept_p=a.basic_acceptance)

    for pc in pc_anneal(iterations=1000):
        pcs.append(pc)
        if len(tmp) == check_len:
            tmp[idx] = pc
            idx = (idx + 1) % check_len
            if m.std_dev(tmp) == 0:
                pcs = pcs[:-int(check_len/2)]
                break
        else:
            tmp.append(pc)

notes = [st.Note(pc, abj.Duration(int(abs(pc*0.125)) + 1, 16))
         for pc in pcs]


# build parts
# TODO: figure out transpositions
insts = [
    {
        'name': 'Clarinet',
        'range': (-10, 24),
        'voice': st.Voice(),
        'transpose': pt.Transposition(2),
        'clef': 'treble'
    },
    {
        'name': 'Viola',
        'range': (-12, 24),
        'voice': st.Voice(),
        'transpose': None,
        'clef': 'alto'
    },
    {
        'name': 'Guitar',
        'range': (-9, 24),
        'voice': st.Voice(),
        'transpose': pt.Transposition(12),
        'clef': 'treble^8'
    },
    {
        'name': 'Bass',
        'range': (-32, 7),
        'voice': st.Voice(),
        'transpose': None,
        'clef': 'bass'
    }
]

# prep instruments
for inst in insts:
    abj.attach(abj.Clef(inst['clef']), inst['voice'])

# pack notes
# TODO intelligent rest packing and note packing
# TODO intelligent harmonization
for note in notes:
    for inst in insts:
        lo, hi = inst['range']
        n = deepcopy(note)
        if n.written_pitch.pitch_number in range(lo, hi):
            if inst['transpose'] is not None:
                n.written_pitch = inst['transpose'](n.written_pitch)
            inst['voice'].append(n)
        else:
            inst['voice'].append(abj.Rest(n.written_duration))

# pack staves
staves = [st.Staff([deepcopy(inst['voice'])]) for inst in insts]
for staff in staves:
    abj.attach(abj.TimeSignature((2, 4)), staff)

# pack score
score = st.Score(staves)

abj.show(score)
