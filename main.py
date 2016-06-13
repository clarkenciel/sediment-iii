import os
import subprocess
import comp_math as m
import anneal as a
import instruments
import utils as u
from datetime import datetime
from abjad import scoretools as st
from copy import deepcopy
from random import random, choice, randrange as rr
from functools import partial
from multiprocessing import Pool
from math import ceil


# pitch class state generator
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


# pitch class energy generator
def pc_energy(goal_pc, dist_f=m.euclid):
    def checker(pc):
        return dist_f([pc], [goal_pc])
    return checker


# generate notes by repeatedly annealing
# and restarting when we reach stability
def collect_pcs(annealer, num_pcs, iterations, num_stable):
    pcs = []
    tmp = []
    idx = 0
    pc_count = 0
    stab_count = 1
    while pc_count < num_pcs:
        bucket = []
        stab_count = num_stable if stab_count >= num_stable else stab_count + 1
        for pc in annealer(iterations=iterations):
            bucket.append(pc)
            pc_count += 1
            if len(tmp) == stab_count:
                tmp[idx] = pc
                idx = (idx + 1) % stab_count
                if m.std_dev(tmp) == 0:
                    pcs.append(bucket[:-int(stab_count/2)])
                    pc_count -= int(stab_count/2)
                    break
            else:
                tmp.append(pc)
    return pcs

# generate our pitches
anchor_pitches = [rr(-12, 12) for _ in range(5)]
pitch_range = (-24, 18)
pc_anneal = a.annealer(temp_f=lambda t: 1 - t,
                       energy_f=pc_energy(choice(anchor_pitches),
                                          m.pitch_distance),
                       state_gen=pc_gen(choice(anchor_pitches),
                                        pitch_range[0],
                                        pitch_range[1]),
                       accept_p=a.basic_acceptance)

pcs = collect_pcs(pc_anneal, 60, 100, 10)
print("pitches collected")

# get our durations
gcd = u.gcd(60, len(pcs))
flat_pcs = [p for pc_b in pcs for p in pc_b]
bucket_durs = u.gen_equal_partitions(60, len(pcs))
pcs = u.partition_equally(gcd, flat_pcs)
pos_pcs = [[((pc % 12) + 1.0) / 24.0 for pc in pc_b]
           for pc_b in pcs]
durs = [[(ceil(pc * (dur / sum(pc_b))), 8) for pc in pc_b]
        for pc_b, dur in zip(pos_pcs, bucket_durs)]
print("durations generated")

# generate notes
notes_prime = [deepcopy(note)
               for pc_coll, dur_coll in zip(pcs, durs)
               for note in list(st.make_notes(pc_coll, dur_coll))]
notes = [u.multiply_by(choice([3]), n)
         if abs(random() - random()) < 0.2 and n.written_duration >= 0.125
         else n
         for n in notes_prime]
print("notes generated")

# build parts
# TODO: figure out transpositions
insts = instruments.get_instrument_dicts(
    'Clarinet', 'Viola', 'Guitar', 'Bass')
print("instruments gotten")

# pack notes
# TODO intelligent harmonization
insts = instruments.pack_instruments(notes, insts)
print("voices packed")

# prep instruments
insts = instruments.prep_instruments(insts)
print("instruments prepped")


# pack staves
maker_pool = Pool(len(insts))
direc = os.curdir + '/' + str(datetime.now())
take_amt = choice([10])
maker = partial(instruments.gen_ly, direc,
                take_amt, (2, 4), (1, 4), anchor_pitches)
print("generating staves")
maker_pool.map(maker, insts)

os.chdir(direc)
subprocess.call(['pdfunite'] +
                [inst['name'] + '_drone.pdf' for inst in insts] +
                [inst['name'] + '_main.pdf' for inst in insts] +
                ['score.pdf'])
