#!/usr/bin/env python3
# Exercises from Laboratory 1


def isLeapYear():
    year = input("Input a year: ")
    if not year % 400:
        print("It's a leap year")
    elif not year % 4 and year % 100:
        print("It's a leap year")
    else:
        print("It's not a leap year")


if __name__ == "__main__":
    a = 23
    b = 12
    c = 43

    if a >= b and a >= c:
        print(a)
    elif b >= a and b >= c:
        print(b)
    else:
        print(c)

    number = input("Enter number to check: ")
    if number % 2:
        print("The number is odd")
    else:
        print("The number is even")

    Tc = input("Enter temperature in Celsius: ")
    Tf = (9/5) * Tc + 32
    print(Tf)
    Tf = input("Enter temperature in Fahrenheit: ")
    Tc = (5/9) * (Tf - 32)
    print(Tc)

    isLeapYear()

    number1 = input("Input number 1: ")
    number2 = input("Input number 2: ")
    number1, number2 = number2, number1
    print(number1, number2)

    checkIfPositive = input("Enter a number: ")
    if checkIfPositive > 0:
        print("Number is positive")
    elif checkIfPositive < 0:
        print("Number is negative")
    else:
        print("Number is 0")
