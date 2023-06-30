#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

test_requirements = ['pytest>=3', ]

setup(
    author="Jozsef Venczeli",
    author_email='jozsi@koffair.com',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="interface and wrapper to run radioship transcipter",
    entry_points={
        'console_scripts': [
            'radioship_transcripter=radioship_transcripter.cli:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='radioship_transcripter',
    name='radioship_transcripter',
    packages=find_packages(include=['radioship_transcripter', 'radioship_transcripter.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/partvishegy/radioship_transcripter',
    version='0.1.0',
    zip_safe=False,
)
