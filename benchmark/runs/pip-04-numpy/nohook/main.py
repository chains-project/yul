import numpy as np


def main():
    array = np.arange(12).reshape(3, 4)
    print("Array:")
    print(array)
    print("Sum:", array.sum())
    print("Mean:", array.mean())
    print("Transpose:")
    print(array.T)


if __name__ == "__main__":
    main()
