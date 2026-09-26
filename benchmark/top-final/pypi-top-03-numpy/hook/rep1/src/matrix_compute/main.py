import numpy as np
from scipy import linalg


def run(size: int = 500, seed: int = 0) -> None:
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((size, size))
    b = rng.standard_normal((size, size))

    product = a @ b
    eigenvalues = np.linalg.eigvals(a)
    inverse = linalg.inv(a)
    det = linalg.det(a)

    print(f"matrix size: {size}x{size}")
    print(f"product shape: {product.shape}")
    print(f"largest eigenvalue magnitude: {np.max(np.abs(eigenvalues)):.4f}")
    print(f"det(a): {det:.4e}")
    print(f"||a @ inv(a) - I||: {np.linalg.norm(a @ inverse - np.eye(size)):.2e}")


if __name__ == "__main__":
    run()
