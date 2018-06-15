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
HDF5 filesystem main function.
'''
import h5py
import fuse
fuse.fuse_python_api = (0, 2)

from h5fslib.dsetnpy import Npy10FsMixin

__all__ = ['main']

def main(mixincls=Npy10FsMixin):
    '''Main entry point that start the HDF5 filesystem server'''
    usage = "\nUserspace HDF5 file explorer.\n\n%prog sourcefile mountpoint"
    class H5FS(mixincls, fuse.Fuse):
        '''merge Fuse + HDF5 interface'''
        pass
    server = H5FS(version="%prog " + fuse.__version__,
                  usage=usage,
                  dash_s_do='setsingle',
                  standard_mods=True,
                  fetch_mp=True)
    server.parse(errex=1)
    _opts, ags = server.cmdline
    if not ags:
        return
    h5file = h5py.File(ags.pop(), 'r')
    try:
        server.h5file = h5file
        server.main()
    finally:
        h5file.close()
