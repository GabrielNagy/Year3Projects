#!/usr/bin/env python3
# Exercises from Laboratory 3

with open('Files/morse.txt', 'r') as morseFile:
    morse = morseFile.read()

morse_dict = {}
morse_list = []

for word in morse.split():
    morse_list.append(word.split(':')[0])

i = iter(morse_list)
morse_dict = dict(zip(i, i))

string = input("Enter message to be translated: ")

for letter in string:
    print(morse_dict[letter.upper()], end=' ')
print('\n')


def square_of_keys():
    d = {}
    for i in range(0, 31):
        d[i] = i*i
    print(d)


square_of_keys()
