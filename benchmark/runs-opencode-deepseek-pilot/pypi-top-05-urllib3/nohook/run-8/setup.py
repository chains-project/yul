from setuptools import find_packages, setup

setup(
    name="httpkit",
    version="0.1.0",
    description="Low-level HTTP client with connection pooling and automatic retries",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=["urllib3>=1.26,<2"],
    extras_require={"test": ["pytest>=6"]},
    entry_points={"console_scripts": ["httpkit=httpkit.__main__:main"]},
)
