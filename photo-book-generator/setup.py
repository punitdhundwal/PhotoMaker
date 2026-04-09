#!/usr/bin/env python3
"""
Setup script for Photo Book Generator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name="photobook-generator",
    version="1.0.0",
    description="Automated Visual Storytelling and Photo Book Generation from Image Collections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Photo Book Generator Team",
    python_requires=">=3.10",
    packages=find_packages(),
    py_modules=[
        'metadata_module',
        'vision_module',
        'layout_module',
        'photobook_generator',
        'main',
    ],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'photobook=main:app',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Printing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="photo book pdf generation computer-vision clustering image-processing",
)
