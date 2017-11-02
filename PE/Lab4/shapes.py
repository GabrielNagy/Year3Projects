from math import sqrt


def area(*side):
    if len(side) == 1:
        return side[0] * side[0]
    elif len(side) == 2:
        return side[0] * side[1]
    elif len(side) == 3:
        s = (side[0] + side[1] + side[2]) / 2
        return sqrt(s * (s - side[0]) * (s - side[1]) * (s - side[2]))
