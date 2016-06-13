import abjad as abj
from abjad import scoretools as st
from copy import deepcopy
from random import choice, randrange as rr
from contextlib import contextmanager
from comp_math import clamp


def pc_to_dur(pc):
    numer = int(abs(pc*0.125)) + 1
    denom = choice([16])
    return abj.Duration(numer, denom)


def match(pred, coll):
    for item in coll:
        if pred(item):
            return True
    return False


def gcd(x, y):
    while y != 0:
        (x, y) = (y, x % y)
    return x


def gen_equal_partitions(dur, num_parts):
    div = gcd(dur, num_parts)
    return [dur / div for _ in range(div)]


def partition_equally(num_parts, coll):
    step = len(coll)/num_parts
    return [coll[n:int((n + 1) * step)] for n in range(num_parts)]


def vary(start_note, n_gens):
    interval = rr(-2, 2)
    pitch = start_note.written_pitch.pitch_number
    dur = start_note.written_duration
    for _ in range(n_gens):
        yield abj.Note(pitch, dur)
        interval = clamp(-12, 12, interval + choice([-1, 1]))
        pitch = pitch + interval


def multiply_by(n, note):
    new_n = deepcopy(note)
    new_n.written_duration /= 4
    tup = abj.Tuplet(abj.Multiplier(2, n), [])
    for varied_note in vary(new_n, n):
        tup.append(varied_note)
    return tup


def get_dur(note_or_tuple):
    if type(note_or_tuple) != abj.Tuplet:
        return float(note_or_tuple.written_duration)
    else:
        return float(note_or_tuple.multiplied_duration)


def take_beats(num, source):
    beat_count = 0
    result = source.__class__()
    for note_or_tuple in source:
        dur = get_dur(note_or_tuple)
        if beat_count + dur == num:
            result.append(deepcopy(note_or_tuple))
            return result
        elif beat_count + dur > num:
            diff = (beat_count + dur) - num
            result.append(abj.Rest(diff))
            return result
        else:
            result.append(deepcopy(note_or_tuple))
            beat_count += dur
    return result
