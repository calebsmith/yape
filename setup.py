#!/usr/bin/python
import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


NAME = 'yape'

setup(
    name=NAME,
    version='0.1',
    author='Caleb Smith',
    author_email='caleb.smithnc@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/calebsmith/' + NAME,
    license='BSD',
    zip_safe=True,
    description="Yet Another Pygame Engine-Framework for 2D tile-based games",
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    install_requires=['pygame'],
    tests_require=[],
    test_suite='runtests',
)
