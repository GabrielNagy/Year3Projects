from math import pi, sqrt


class Shape:
    def __init__(self):
        pass

    def display(self):
        print(type(self).__name__)

    def getarea(self):
        pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def getarea(self):
        return (pi * self.radius) ** 2


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def getarea(self):
        return self.side ** 2


class Rectangle(Shape):
    def __init__(self, side1, side2):
        self.side1 = side1
        self.side2 = side2

    def getarea(self):
        return self.side1 * self.side2


class Triangle(Shape):
    def __init__(self, side1, side2, side3):
        self.side1 = side1
        self.side2 = side2
        self.side3 = side3

    def getarea(self):
        s = (self.side1 + self.side2 + self.side3) / 2
        return sqrt(s * (s - self.side1) * (s - self.side2) * (s - self.side3))


def show_menu():
    print("""Enter the shape for which you want to compute the area:
        1. Square
        2. Rectangle
        3. Triangle
        4. Circle""")


def get_circle_radius():
    radius = float(input("Enter the radius of the circle: "))
    if radius <= 0:
        raise ValueError("Numbers must be positive")
    circle = Circle(radius)
    print(circle.getarea())


def get_square_sides():
    side = float(input("Enter the side of the square: "))
    if side <= 0:
        raise ValueError("Numbers must be positive")
    square = Square(side)
    print(square.getarea())


def get_rectangle_sides():
    side1 = float(input("Enter the first side of the rectangle: "))
    side2 = float(input("Enter the second side of the rectangle: "))
    if min(side1, side2) <= 0:
        raise ValueError("Numbers must be positive")
    rectangle = Rectangle(side1, side2)
    print(rectangle.getarea())


def get_triangle_sides():
    side1 = float(input("Enter the first side of the triangle: "))
    side2 = float(input("Enter the second side of the triangle: "))
    side3 = float(input("Enter the third side of the triangle: "))
    if min(side1, side2, side3) <= 0:
        raise ValueError("Numbers must be positive")
    triangle = Triangle(side1, side2, side3)
    print(triangle.getarea())


if __name__ == "__main__":
    show_menu()
    options = {1: get_square_sides, 2: get_rectangle_sides, 3: get_triangle_sides, 4: get_circle_radius}
    user_input = int(input("Input a number: "))
    if user_input in options.keys():
        exec_function = options.get(user_input)
    else:
        raise ValueError("Invalid option")
    exec_function()
