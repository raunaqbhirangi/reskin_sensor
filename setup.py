import os
import sys
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='reskin_sensor',
    version='1.0.0',
    author='Raunaq Bhirangi',
    author_email="rbhirang@andrew.cmu.edu",
    description='Data acquisition library for a ReSkin sensor',
    long_description=read('README.md'),
    packages=find_packages(),
    url="https://github.com/raunaqbhirangi/reskin_sensor.git",
)