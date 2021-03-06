# Copyright (C) 2019 Blu Wireless Ltd.
# All Rights Reserved.
#
# This file is part of BLADE.
#
# BLADE is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# BLADE is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# BLADE.  If not, see <https://www.gnu.org/licenses/>.
#

import os

from setuptools import setup

this_dir = os.path.abspath(os.path.dirname(__file__))
top_dir  = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Calculate relative package path
pkg_path = os.path.relpath(this_dir, os.getcwd())

# Calculate path to README.md
readme_path      = os.path.join(top_dir, "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r") as fh:
        long_description = fh.read()

setup(
    name="designformat",
    version="1.3",
    license='GNU General Public License v3.0',
    description=
        "A Cross-Language Interchange Format for Hardware Description Based on "
        "JSON"
    ,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Blu Wireless Ltd',
    url='https://www.bluwireless.com',
    project_urls={
        'Source': 'https://github.com/bluwireless/designformat',
        'Tracker': 'https://github.com/bluwireless/designformat/issues',
        'Documentation': 'https://designformat.readthedocs.io/en/latest',
    },
    packages=['designformat'],
    package_dir={ '': pkg_path },
    extras_require={
        "documentation": [
            'sphinx',
            'recommonmark',
            'sphinx-markdown-tables',
            'sphinx-rtd-theme',
            'sphinx-js',
        ],
    },
)
