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
HDF5 filesystem implementation with datasets as .npy files
'''
import os.path as osp
from StringIO import StringIO
import h5py

from numpy.lib.format import write_array_header_1_0 as hwrite, \
                             header_data_from_array_1_0 as hdata, \
                             magic

from h5fslib.dsetbitstream import BitStreamFsMixin


__all__ = ['Npy10FsMixin']

class Npy10FsMixin(BitStreamFsMixin):
    '''Implement the HDF5 filesytem interface with dataset exported as
    .npy file version 1.0
    '''
    # XXX: There is a problematic case when a subgroup named
    # 'a.npy' and a dataset named 'a' have the same parent
    file_extension = 'npy'

    @staticmethod
    def _get_npy_header(h5entry):
        header = StringIO()
        header.write(magic(1, 0)) # XXX: support only 1.0 version of npy file
        hwrite(header, hdata(h5entry.value))
        return header.getvalue()

    # ===

    def get_entry(self, path):
        '''Return the entry recorded at ``path`` or raise H5IOError'''
        trailling = osp.extsep + self.file_extension
        if path.endswith(trailling):
            path = path[:-len(trailling)]
        return super(Npy10FsMixin, self).get_entry(path)

    def get_name(self, h5entry):
        '''Return the entry file name as string'''
        # XXX unicode deos not seems to be allowed
        name = super(Npy10FsMixin, self).get_name(h5entry)
        if isinstance(h5entry, h5py.highlevel.Dataset):
            name = osp.extsep.join((name, self.file_extension))
        return name

    def get_size(self, h5entry):
        '''Return the byte size of the file'''
        header_size = len(self._get_npy_header(h5entry))
        data_size = super(Npy10FsMixin, self).get_size(h5entry)
        return header_size + data_size

    def get_data(self, h5entry, start, end):
        '''Return a slice of data data from start to end'''
        header = self._get_npy_header(h5entry)
        header_size = len(header)
        data = []
        if start < header_size:
            data.append(header[start:end])
            start = 0
        else:
            start -= header_size
        end -= header_size
        if end > 0:
            data.append(super(Npy10FsMixin, self).get_data(h5entry, start, end))
        return ''.join(data)
