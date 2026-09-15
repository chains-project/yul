import numpy as np


def main() -> None:
    rng = np.random.default_rng(seed=0)

    a = rng.standard_normal((500, 500))
    b = rng.standard_normal((500, 500))

    product = a @ b
    eigenvalues = np.linalg.eigvals(a)
    sign, logdet = np.linalg.slogdet(a)
    inverse = np.linalg.inv(a)
    norm = np.linalg.norm(product)

    print(f"product shape: {product.shape}")
    print(f"largest eigenvalue magnitude: {np.max(np.abs(eigenvalues)):.4f}")
    print(f"determinant: sign={sign:.0f}, log|det|={logdet:.4f}")
    print(f"inverse check (max |A @ A^-1 - I|): {np.max(np.abs(a @ inverse - np.eye(a.shape[0]))):.2e}")
    print(f"product norm: {norm:.4f}")


if __name__ == "__main__":
    main()
