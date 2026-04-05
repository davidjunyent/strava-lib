#!/usr/bin/env python3
"""Setup configuration for strava-lib package."""

from setuptools import setup, find_packages

setup(
    name="strava-lib",
    version="0.1.0",
    description="Shared library for Strava integration projects",
    author="David Junyent",
    author_email="d.junyent@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
