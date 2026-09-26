import numpy as np


def main() -> None:
    rng = np.random.default_rng(seed=0)
    a = rng.standard_normal((500, 500))
    b = rng.standard_normal((500, 500))

    product = a @ b
    eigenvalues = np.linalg.eigvals(a @ a.T)
    inverse = np.linalg.inv(a + np.eye(a.shape[0]))

    print(f"product shape: {product.shape}")
    print(f"largest eigenvalue: {eigenvalues.max():.4f}")
    print(f"inverse trace: {np.trace(inverse):.4f}")


if __name__ == "__main__":
    main()
