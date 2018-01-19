if __name__ == "__main__":
    text = '''Now is the winter of our discontent
Made glorious summer by this sun of York;
And all the clouds that lour'd upon our house
In the deep bosom of the ocean buried.'''
    text = text.replace(';', '').replace('\'', '').replace('.', '').split()
    filtered = list(filter(lambda x: len(x) >= 4, text))
    print(filtered)
