import abjad as abj
from abjad import scoretools as st
from copy import deepcopy
from random import choice


def smart_breaks(dur_size, dur_base, notes):
    expanded_notes = []
    thunk_base = dur_base
    thunk_size = abj.Duration(dur_size, thunk_base)  # each thunk is 4 16ths
    running_thunk_count = abj.Duration(0, thunk_base)
    for note in notes:
        n = deepcopy(note)
        n_dur = note.written_duration
        check_sum = running_thunk_count + float(n_dur)
        if check_sum < float(thunk_size):
            expanded_notes.append(n)
            running_thunk_count += n_dur
        elif check_sum == float(thunk_size):
            expanded_notes.append(n)
            running_thunk_count = abj.Duration(0, thunk_base)
        else:
            # overflow part
            sub_two = (running_thunk_count + n_dur) - thunk_size
            # primary part
            sub_one = n_dur - sub_two
            sub_n_one = st.Note(n.written_pitch, sub_one)
            sub_n_two = st.Note(n.written_pitch, sub_two)
            expanded_notes.append(sub_n_one)
            expanded_notes.append(sub_n_two)
            running_thunk_count = sub_two
    return expanded_notes


def pc_to_dur(pc):
    numer = int(abs(pc*0.125)) + 1
    denom = choice([16])
    return abj.Duration(numer, denom)


def merge_rests(dur_size, dur_base, notes):
    return [deepcopy(n) for n in notes]
