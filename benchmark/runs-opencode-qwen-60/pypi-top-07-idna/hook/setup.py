from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="idna-tool",
    version="1.0.0",
    description="Encode and decode internationalized domain names per the IDNA specification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Developer",
    author_email="dev@example.com",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "idna>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "idna-tool=idna_tool.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)