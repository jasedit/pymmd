"""Setuptools file for a MultiMarkdown Python wrapper."""
from codecs import open
from os import path
from distutils.core import setup
from setuptools import find_packages


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pymmd',
    version='0.0.1',
    description='Python wrapper for the MultiMarkdown library.',
    long_description=long_description,
    license='MIT',
    author='Jason Ziglar',
    author_email='jasedit@gmail.com',
    url="https://github.com/jasedit/pymmd",
    classifiers=[
        'Development Status :: 3',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Filters',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages()
    )
