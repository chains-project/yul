import numpy as np


def main() -> None:
    rng = np.random.default_rng(seed=0)

    a = rng.standard_normal((1000, 1000))
    b = rng.standard_normal((1000, 1000))

    product = a @ b
    eigenvalues = np.linalg.eigvalsh(a @ a.T)
    inverse = np.linalg.inv(a + np.eye(a.shape[0]))

    print("Matrix product shape:", product.shape)
    print("Largest eigenvalue:", eigenvalues[-1])
    print("Inverse trace:", np.trace(inverse))


if __name__ == "__main__":
    main()
