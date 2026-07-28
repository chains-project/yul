import numpy as np


def summarize(array: np.ndarray) -> dict:
    return {
        "shape": array.shape,
        "mean": float(array.mean()),
        "std": float(array.std()),
        "min": float(array.min()),
        "max": float(array.max()),
    }


def main() -> None:
    rng = np.random.default_rng(seed=0)
    data = rng.normal(loc=0.0, scale=1.0, size=(1000, 10))

    normalized = (data - data.mean(axis=0)) / data.std(axis=0)
    correlation = np.corrcoef(normalized, rowvar=False)

    print("Data summary:", summarize(data))
    print("Correlation matrix shape:", correlation.shape)


if __name__ == "__main__":
    main()
