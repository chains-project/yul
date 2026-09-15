import numpy as np


def main() -> None:
    rng = np.random.default_rng(seed=0)

    a = rng.standard_normal((512, 512))
    b = rng.standard_normal((512, 512))

    product = a @ b
    eigenvalues = np.linalg.eigvals(a)
    inverse = np.linalg.inv(a)
    sign, logdet = np.linalg.slogdet(a)

    print(f"product shape: {product.shape}")
    print(f"largest eigenvalue magnitude: {np.max(np.abs(eigenvalues)):.4f}")
    print(f"log|determinant|: {logdet:.4f} (sign={sign:.0f})")
    print(f"inverse check (max |A @ A^-1 - I|): {np.max(np.abs(a @ inverse - np.eye(512))):.2e}")


if __name__ == "__main__":
    main()
