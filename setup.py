#!/usr/bin/env python

"""Setup script for the radioship_transcriber."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = ["torch==1.12.1",
        "huggingsound",
        "pydub",
        "ffmpeg",
        "ffprobe",
        "inaspeechsegmenter",]

dev_requirements = {
        "dev": [
            "cookiecutter",
            "pytest",
            "pre-commit",
            "black",
            "pylint",
            "mypy",
            "coverage",
            "huggingface-hub[cli]",
        ]
    }

test_requirements = [
    "pytest>=7",
]

setup(
    author="Jozsef Venczeli",
    author_email="venczeli.jozsef@gmail.com",
    python_requires=">=3.10.10",

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    description="Interface and wrapper to run radioship_transcriber",
    entry_points={
        "console_scripts": [
            "radioship_transcriber=radioship_transcriber.cli:main",
        ],
    },
    install_requires=requirements,
    extras_require = dev_requirements,
    license="BSD license",
    include_package_data=True,
    keywords="radioship_transcriber",
    name="radioship_transcriber",
    packages=find_packages(
        include=["radioship_transcriber", "radioship_transcriber.*"]
    ),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/Koffair/radioship_transcriber",
    version="0.1.0",
    zip_safe=False,
)
