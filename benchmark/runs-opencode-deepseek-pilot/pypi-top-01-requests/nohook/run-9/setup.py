from setuptools import find_packages, setup

with open("README.md", "r") as handle:
    long_description = handle.read()

setup(
    name="api-fetcher",
    version="0.1.0",
    description="Fetch data from a REST API over HTTP.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=["requests>=2.20"],
    extras_require={"dev": ["pytest>=6.0"]},
    entry_points={
        "console_scripts": ["api-fetcher=api_fetcher.__main__:main"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
