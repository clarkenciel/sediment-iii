from math import sqrt


def nearest_power_of(comp_val, tgt_val):
    """Find the power of comp_val that is nearest to
    tgt_val"""
    result = comp_val  # assume we start as close as possible
    last_dist = abs(comp_val - tgt_val)
    power = 2
    while abs(comp_val ** power - tgt_val) < last_dist:
        last_dist = abs(comp_val ** power - tgt_val)
        result = comp_val ** power
        power += 1
    return result


def iterate_until(pred, f, val):
    """Produce a list of values that are the result
    of repeatedly applying f to val, and then the results
    of that application, until evaluating the predicate with
    one of these results returns False"""
    new_coll = [f(val)]
    while pred(f(new_coll[-1])) is False:
        new_coll.append(f(new_coll[-1]))
    return new_coll


def clamp(lo_lim, hi_lim, x):
    if x < lo_lim:
        return lo_lim
    elif x > hi_lim:
        return hi_lim
    else:
        return x


def to_scale(from_lo, from_hi, to_lo, to_hi, val):
    val_pos = (val - from_lo) / (from_hi - from_lo)
    return to_lo + (val_pos * (to_hi - to_lo))


def sign(val):
    if val > 0:
        return 1
    elif val < 0:
        return -1
    else:
        return 0


def std_dev(vals):
    n = len(vals)
    avg = sum(vals) / n
    squared_deviance = [(v - avg) ** 2 for v in vals]
    squared_dev_avg = sum(squared_deviance) / n
    return sqrt(squared_dev_avg)


def covariance(vals1, vals2):
    """Covariance between to 'random' variables.
    ASSUMES EQUAL LENGTHS"""
    n = len(vals1)
    avg_x, avg_y = sum(vals1) / n, sum(vals2) / n
    variance_x = [v - avg_x for v in vals1]
    variance_y = [v - avg_y for v in vals2]
    dot = [x * y for x, y in zip(variance_x, variance_y)]
    return sum(dot) / n


# SOME DISTANCE MEASURES
def pearson(vals1, vals2):
    return covariance(vals1, vals2) / (std_dev(vals1) * std_dev(vals2))


def euclid(vals1, vals2):
    return sum([(y - x) ** 2 for x, y in zip(vals1, vals2)])


def pitch_distance(p1, p2):
    pc1, pc2 = p1[0], p2[0]
    mod_dist = (pc2 % 12) - (pc1 % 12)
    return mod_dist + (pc2 - pc1)
