import abjad as abj
from abjad import scoretools as st
from abjad.tools import pitchtools as pt
from abjad.tools import schemetools as scht
from abjad.tools.topleveltools import set_
from copy import deepcopy


def lookup_by_name(comp_val, coll):
    for x in coll:
        if x['name'] == comp_val:
            return x
    return None


def get_instrument_dicts(*instrument_names):
    inst_list = [
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

    return [deepcopy(inst)
            for inst in [lookup_by_name(name, inst_list)
                         for name in instrument_names]
            if inst is not None]


def pack_instruments(notes, instrument_dicts):
    insts = deepcopy(instrument_dicts)
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
    return insts


def prep_instruments(instrument_dicts):
    insts = instrument_dicts  # deepcopy(instrument_dicts)
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


def make_staff(ts_tuple, rewrite_tuple, instrument_dict):
    staff = st.Staff([instrument_dict['voice']])
    merge_rests(abj.TimeSignature(rewrite_tuple), staff)
    abj.attach(abj.TimeSignature(ts_tuple), staff)
    return staff
