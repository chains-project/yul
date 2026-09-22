from setuptools import find_packages, setup

setup(
    name="http-client",
    version="0.1.0",
    description="Low-level HTTP client with connection pooling and automatic retries",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.6",
    install_requires=["urllib3>=1.26,<2"],
    entry_points={"console_scripts": ["http-client=main:main"]},
)
