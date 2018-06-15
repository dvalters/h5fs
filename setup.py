#! /usr/bin/env python

# Copyright (C) 2012-2013  Alain Leufroy <contact@logilab.fr>
#
# This file is part of h5fs.
#
# h5fs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# h5fs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with h5fs.  If not, see <http://www.gnu.org/licenses/>.

import sys
from distutils.core import setup

setup(
    name = 'h5fs',
    version = '0.1.0',
    author = 'alain leufroy',
    author_email = 'contact@logilab.fr',
    description = 'A virtual filesystem that exposes the content of HDF5 files',
    long_description = open("README").read(),
    packages = ['h5fslib'],
    scripts = ['bin/h5fs'],
)
