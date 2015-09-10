#!/usr/bin/env python
from setuptools import setup, find_packages

PROJECT = 'cinderdiags'

# Change docs/sphinx/conf.py too!
VERSION = '0.1'

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Cinder Diagnostics CLI',
    long_description=long_description,

    author='TBD',
    author_email='TBD',

    url='TBD',
    download_url='TBD',

    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Intended Audience :: Cinder admins',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=[
        'cliff', 'cliff-tablib', 'hp3parclient', 'oslo.utils', 'paramiko'
    ],

    namespace_packages=[],
    packages=find_packages(),
    package_data={
        '': ['*.conf']
    },
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'cinderdiags = cinderdiags.main:main'
        ],
        'cliff.cinderdiags': [
            'options-check = cinderdiags.array:CheckArray',
            'software-check = cinderdiags.software:CheckSoftware'
        ],
    },

    zip_safe=False,
)
