from math import sqrt


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
