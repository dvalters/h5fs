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

'''
HDF5 filesystem implementation.
'''
from h5fslib.core import FsMixin


__all__ = ['BitStreamFsMixin']

class BitStreamFsMixin(FsMixin):
    '''Implement the HDF5 filesytem interface with dataset exported as bitstream
    file.'''

    @staticmethod
    def get_size(h5entry):
        '''Return the byte size of the file'''
        arr = h5entry.value
        return arr.itemsize * arr.size

    @staticmethod
    def get_data(h5entry, start, end):
        '''Return a slice of data from start to end'''
        return h5entry.value.data[start:end]
