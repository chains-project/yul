"""Setup script for date-arith package."""
from setuptools import setup, find_packages

setup(
    name="date-arith",
    version="0.1.0",
    description="Parse flexible date strings and compute relative date arithmetic",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "date-arith=date_arith.cli:main",
        ],
    },
)