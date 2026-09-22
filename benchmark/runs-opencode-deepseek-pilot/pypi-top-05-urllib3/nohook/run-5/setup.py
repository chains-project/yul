from setuptools import find_packages, setup

with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f if line.strip()]

setup(
    name="http-client",
    version="0.1.0",
    description="Low-level HTTP client with connection pooling and automatic retries",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.6",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "http-client=http_client.cli:main",
        ],
    },
)
