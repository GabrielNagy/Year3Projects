#!/usr/bin/env python3
import shapes


def show_menu():
    print("""Enter the shape for which you want to compute the area:
        1. Square
        2. Rectangle
        3. Triangle""")


def get_square_sides():
    side = int(input("Enter the side of the square: "))
    return side


def get_rectangle_sides():
    side1 = int(input("Enter the first side of the rectangle: "))
    side2 = int(input("Enter the second side of the rectangle: "))
    return side1, side2


def get_triangle_sides():
    side1 = int(input("Enter the first side of the triangle: "))
    side2 = int(input("Enter the second side of the triangle: "))
    side3 = int(input("Enter the third side of the triangle: "))
    return side1, side2, side3


if __name__ == "__main__":
    show_menu()
    number = input("Enter a number: ")
    if number == '1':
        print(shapes.square_area(*get_square_sides()))
    elif number == '2':
        print(shapes.rectangle_area(*get_rectangle_sides()))
    elif number == '3':
        print(shapes.triangle_area(*get_triangle_sides()))
    else:
        raise ValueError("Invalid number provided")
