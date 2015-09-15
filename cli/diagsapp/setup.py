#  (c) Copyright 2015 Hewlett Packard Enterprise Development LP
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
        'cliff', 'cliff-tablib', 'hp3parclient', 'paramiko'
    ],

    namespace_packages=[],
    packages=find_packages(),
    # package_data={
    #     '': ['config/*.conf']
    # },
    data_files=[('config', ['config/cli.conf'])],
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
