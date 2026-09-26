import numpy as np


def main() -> None:
    rng = np.random.default_rng(seed=0)
    a = rng.standard_normal((500, 500))
    b = rng.standard_normal((500, 500))

    product = a @ b
    eigenvalues = np.linalg.eigvals(a)
    inverse = np.linalg.inv(a)

    print("Matrix product shape:", product.shape)
    print("Largest eigenvalue magnitude:", np.max(np.abs(eigenvalues)))
    print("Reconstruction error:", np.max(np.abs(a @ inverse - np.eye(a.shape[0]))))


if __name__ == "__main__":
    main()
