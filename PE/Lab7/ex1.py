def menu():
    print("Enter the desired conversion:")
    print("1. From Celsius to Fahrenheit")
    print("2. From Fahrenheit to Celsius")


def error_handler():
    print("Inexistent option, try again")


def convert_to_fahrenheit():
    temperatures = list(input("Enter the temperatures to be converted: "))
    new_temperatures = list(map(lambda x: ((9 / 5) * x + 32), temperatures))
    print(new_temperatures)


def convert_to_celsius():
    temperatures = list(input("Enter the temperatures to be converted: "))
    new_temperatures = list(map(lambda x: (5 / 9) * (x - 32), temperatures))
    print(new_temperatures)


if __name__ == "__main__":
    menu()
    options = {1: convert_to_fahrenheit, 2: convert_to_celsius}
    user_input = int(input("Input a number: "))
    exec_function = options.get(user_input, error_handler)
    exec_function()
