def generateFile(filename='data.txt', size=512_000) -> None:
    # default 500 KB
    with open(filename, 'wt') as file:
        data = 's' * size
        file.write(data)


if __name__ == "__main__":
    generateFile()
