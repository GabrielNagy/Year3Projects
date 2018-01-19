from functools import reduce


if __name__ == "__main__":
    l = [12, 32, 1, 73, 25, 68, 83, 29, 55, 61, 100, 97, 2]
    print(reduce((lambda x, y: x if x >= y else y), l))
