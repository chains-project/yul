import numpy as np


def run_demo(size: int = 500, seed: int = 0) -> None:
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((size, size))
    b = rng.standard_normal((size, size))

    product = a @ b
    eigenvalues = np.linalg.eigvals(a[:50, :50])
    inverse = np.linalg.inv(a[:50, :50])

    print(f"matmul result shape: {product.shape}")
    print(f"matmul result norm:  {np.linalg.norm(product):.4f}")
    print(f"eigenvalue mean:     {eigenvalues.mean():.4f}")
    print(f"inverse trace:       {np.trace(inverse):.4f}")


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
