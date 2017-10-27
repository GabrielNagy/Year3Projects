#!/usr/bin/env python3
# Exercises from Laboratory 2


def count_words(text):
    counter = 0
    for word in text.split():
        counter += 1
    return counter


def count_vowels(text):
    counter = 0
    vowels = "aeiouAEIOU"
    for letter in text:
        if letter in vowels:
            counter += 1
    return counter


def factorial(number):
    if number == 0:
        return 1
    else:
        return number * factorial(number-1)


if __name__ == "__main__":
    text = """Now is the winter of our discontent
    Made glorious summer by this sun of York;
    And all the clouds that lour'd upon our house
    In the deep bosom of the ocean buried."""

    print("Number of words: %d" % count_words(text))
    print("Number of vowels: %d" % count_vowels(text))

    list = ['Monty', 'Python', 'and', 'the', 'Holy', 'Grail']
    print(list[::-1])

    string = input("Enter string: ")
    if string == string[::-1]:
        print("Entered string is palindrome.")
    else:
        print("Entered string is not a palindrome.")

    list1 = [1, 2, 3, 4, 5, 6, 7, 8]
    list2 = [2, 4, 9, 11, 33]
    list3 = []

    for element in list1:
        if element in list2:
            list3.append(element)
    print(list3)

    divList = []
    for i in range(1000, 2000):
        if i % 5 and not i % 7:
            divList.append(i)
    print(divList)

    number = int(input("Enter number to compute factorial: "))
    print("The factorial of the number is %d" % factorial(number))

    numberArray = [10, 20, 20, 30, 30, 56, 67, 75, 22, 10, 33]
    numberArray = set(numberArray)
    numberArray.remove(max(numberArray))
    numberArray.remove(min(numberArray))
    print(numberArray)
    print(sum(numberArray) / float(len(numberArray)))
