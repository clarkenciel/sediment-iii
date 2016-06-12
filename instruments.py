import os
import subprocess
import abjad as abj
from abjad import scoretools as st
from abjad import topleveltools as tlt
from abjad.tools import pitchtools as pt
from abjad.tools import schemetools as scht
from abjad.tools.topleveltools import set_
from abjad.tools import lilypondfiletools as lyft
from copy import deepcopy
from contextlib import contextmanager


def lookup_by_name(comp_val, coll):
    for x in coll:
        if x['name'] == comp_val:
            return x
    return None


def range_tuple(start_str, stop_str):
    return tuple([n.written_pitch.pitch_number
                  for n in st.make_notes([start_str, stop_str], (1, 4))])


def get_instrument_dicts(*instrument_names):
    inst_list = [
        {
            'name': 'Clarinet',
            'range': range_tuple("d", "c'''"),
            'voice': st.Voice(),
            'transpose': pt.Transposition(2),
            'clef': 'treble'
        },
        {
            'name': 'Viola',
            'range': range_tuple("c", "c'''"),
            'voice': st.Voice(),
            'transpose': None,
            'clef': 'alto'
        },
        {
            'name': 'Guitar',
            'range': range_tuple("e,", "e''"),
            'voice': st.Voice(),
            'transpose': None,  # pt.Transposition(12),
            'clef': 'treble_8'
        },
        {
            'name': 'Bass',
            'range': range_tuple("e,,", "g'"),
            'voice': st.Voice(),
            'transpose': None,
            'clef': 'bass'
        }
    ]

    return [deepcopy(inst)
            for inst in [lookup_by_name(name, inst_list)
                         for name in instrument_names]
            if inst is not None]


@contextmanager
def transposition(inst, n):
    if inst['transpose'] is not None:
        n.written_pitch = inst['transpose'](n.written_pitch)
    yield n


@contextmanager
def inst_range(inst, n):
    lo, hi = inst['range']
    if n.written_pitch.pitch_number in range(lo, hi):
        yield n
    else:
        yield abj.Rest(n.written_duration)


def add_note_to_inst(inst, n):
    with transposition(inst, n) as n:
        with inst_range(inst, n) as n_or_r:
            inst['voice'].append(n_or_r)


def all_rests(tup):
    for n in list(tup):
        if type(n) != abj.Rest:
            return False
    return True


def add_tup_to_inst(inst, tup):
    new_tup = abj.Tuplet(tup.multiplier, [])
    for note in list(tup):  # for some reason tups don't iterate well??
        with transposition(inst, note) as note:
            with inst_range(inst, note) as note:
                new_tup.append(note)
    if all_rests(new_tup):
        inst['voice'].append(abj.Rest(new_tup.multiplied_duration))
    else:
        inst['voice'].append(new_tup)


def add_note_or_tup_to_inst(inst, n_or_t):
    if type(n_or_t) == abj.Note:
        add_note_to_inst(inst, n_or_t)
    else:
        add_tup_to_inst(inst, n_or_t)


def pack_instruments(notes, instrument_dicts):
    insts = deepcopy(instrument_dicts)
    for note in deepcopy(notes):
        for inst in insts:
            n = deepcopy(note)
            add_note_or_tup_to_inst(inst, n)
    return insts


def prep_instruments(instrument_dicts):
    insts = deepcopy(instrument_dicts)
    for inst in insts:
        abj.attach(abj.Clef(inst['clef']), inst['voice'])
        inst['voice'].remove_commands.append('Note_heads_engraver')
        inst['voice'].consists_commands.append('Completion_heads_engraver')
        inst['voice'].remove_commands.append('Rest_engraver')
        inst['voice'].consists_commands.append('Completion_rest_engraver')
        set_(inst['voice']).beam_exceptions = scht.SchemeVector()
        set_(inst['voice']).base_moment = scht.SchemeMoment(1, 4)
        set_(inst['voice']).beat_structure = scht.SchemeVector(1, 1)
        set_(inst['voice']).completion_unit = scht.SchemeMoment(1, 4)
    return insts


def merge_rests(time_signature, staff):
    for shard in abj.mutate(staff[:]).split([time_signature], cyclic=True):
        abj.mutate(shard).rewrite_meter(time_signature)


def apply_techniques(instrument_dict):
    pass


def make_main_staff(ts_tuple, rewrite_tuple, instrument_dict):
    tmp = st.Staff([instrument_dict['voice']])
    merge_rests(abj.TimeSignature(rewrite_tuple), tmp)
    staff = abj.Staff()
    for x in tmp[:30]:
        staff.append(deepcopy(x))
    print(instrument_dict['name'])
    print(len(staff))
    abj.attach(abj.TimeSignature(ts_tuple), staff)
    abj.attach(abj.Clef(instrument_dict['clef']), staff)

    return staff


def make_drone_staff(anchor_tones, instrument_dict):
    staff = abj.Staff()
    for tone in anchor_tones:
        m = abj.Measure((1, 1), [abj.Note(tone, abj.Duration(1, 1))])
        tlt.override(staff).time_signature.stencile = False
        staff.append(m)
        staff.append(m)
    return staff


def make_page(direc, main_staff, drone_staff, inst):
    mfn = direc + '/' + inst['name'] + '_main.ly'
    dfn = direc + '/' + inst['name'] + '_drone.ly'

    main_group = st.StaffGroup([main_staff])
    drone_group = st.StaffGroup([drone_staff])
    for group in [main_group, drone_group]:
        tlt.override(group).system_start_bracket.collapse_height = 2000

    score1 = st.Score([main_group])
    score2 = st.Score([drone_group])
    for score in [score1, score2]:
        tlt.override(score).staff_grouper.staffgroup_staff_spacing = \
            scht.SchemeAssociativeList(('basic-distance', 30), ('padding', 1))
        tlt.override(score).bar_line.allow_span_bar = False
        tlt.override(score).system_start_bar.collapse_height = 2000

    mf = lyft.make_basic_lilypond_file(score1)
    df = lyft.make_basic_lilypond_file(score2)

    for fn, lf in zip([mfn, dfn], [mf, df]):
        with open(fn, 'w+') as f:
            f.write(format(lf))
    return mfn, dfn


def gen_ly(direc, ts_tuple, rewrite_tuple, anchor_tones, inst):
    if not os.path.isdir(direc):
        os.makedirs(direc)
    main_staff = make_main_staff(ts_tuple, rewrite_tuple, inst)
    drone_staff = make_drone_staff(anchor_tones, inst)
    mfn, dfn = make_page(direc, main_staff, drone_staff, inst)
    os.chdir(direc)
    subprocess.call(['lilypond', mfn, dfn])
    print('done with', inst['name'], mfn, dfn)
