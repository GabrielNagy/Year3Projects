from math import sqrt


def square_area(side):
    return side * side


def rectangle_area(side1, side2):
    return side1 * side2


def triangle_area(side1, side2, side3):
    s = (side1 + side2 + side3) / 2
    return sqrt(s * (s - side1) * (s - side2) * (s - side3))
