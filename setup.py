"""Setup script for backward compatibility with pip install.

This file allows the package to be installed with 'pip install .'
while the primary development workflow uses Poetry.
"""

from setuptools import find_packages, setup

# Read version from package
with open("charcoal/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

# Read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="charcoal",
    version=version,
    description="A Python CLI for stacked pull requests and branch management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daner Williams",
    author_email="danerwilliams@example.com",
    url="https://github.com/danerwilliams/charcoal",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.11",
    install_requires=[
        "click>=8.1.0",
        "pydantic>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0",
            "pytest-xdist>=3.0",
            "mypy>=1.0",
            "ruff>=0.1.0",
            "black>=24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gt=charcoal.__main__:cli",
            "graphite=charcoal.__main__:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
