import numpy as np


def main() -> None:
    rng = np.random.default_rng(seed=0)
    a = rng.standard_normal((4, 4))
    b = rng.standard_normal((4, 4))

    product = a @ b
    eigenvalues = np.linalg.eigvals(product)
    inverse = np.linalg.inv(product)

    print("A @ B =\n", product)
    print("Eigenvalues:\n", eigenvalues)
    print("Inverse:\n", inverse)


if __name__ == "__main__":
    main()
