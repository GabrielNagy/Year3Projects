#!/usr/bin/env python3
import shapes


def show_menu():
    print("""Enter the shape for which you want to compute the area:
        1. Square
        2. Rectangle
        3. Triangle""")


def sides(option):
    side = []
    for i in range(option):
        side.append(float(input("Enter side %d: " % (i+1))))
        if side[i] <= 0:
            raise ValueError("Numbers must be positive")
    return side


def get_square_sides():
    side = float(input("Enter the side of the square: "))
    if side <= 0:
        raise ValueError("Numbers must be positive")
    return side


def get_rectangle_sides():
    side1 = float(input("Enter the first side of the rectangle: "))
    side2 = float(input("Enter the second side of the rectangle: "))
    if min(side1, side2) <= 0:
        raise ValueError("Numbers must be positive")
    return side1, side2


def get_triangle_sides():
    side1 = float(input("Enter the first side of the triangle: "))
    side2 = float(input("Enter the second side of the triangle: "))
    side3 = float(input("Enter the third side of the triangle: "))
    if min(side1, side2, side3) <= 0:
        raise ValueError("Numbers must be positive")
    return side1, side2, side3


if __name__ == "__main__":
    show_menu()
    number = int(input("Enter a number: "))
    if number in [1, 2, 3]:
        print(shapes.area(*sides(number)))
    else:
        raise ValueError("Invalid number provided")
