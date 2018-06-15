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

import os
import os.path as osp
import stat
import errno
from itertools import imap, chain
from functools import partial


import h5py

import fuse

__all__ = ['FsMixin']

class H5IOError(IOError):
    """Raised when a bad hdf5 entry was given"""
    # OSError and IOError are converted to errno by fuse.ErrnoWrapper

class Stat(fuse.FuseStruct): # pylint: disable-msg=R0903
    "Fill up stat attributes with user acces"
    st_mode  = None
    st_ino   = 0
    st_dev   = 0
    st_nlink = None
    st_uid   = os.getuid()
    st_gid   = os.getgid()
    st_size  = 0
    st_atime = 0
    st_mtime = 0
    st_ctime = 0


class GroupStat(Stat): # pylint: disable-msg=R0903
    "Fill up stat attributes with user acces for Groups"
    st_mode = stat.S_IFDIR | stat.S_IREAD | stat.S_IEXEC
    st_nlink = 1


class DatasetStat(Stat): # pylint: disable-msg=R0903
    "Fill up stat attributes with user acces for Groups"
    st_mode = stat.S_IFREG | stat.S_IREAD
    st_nlink = 1


# TODO: h5file.id.get_comment() ...
class FsMixin(object):
    '''Implement the HDF5 filesytem interface'''

    h5file = None

    def get_entry(self, path):
        '''Return the hdf5 entry exposed at ``path`` in the fs or raise
        H5IOError'''
        try:
            h5entry = self.h5file[path]
        except KeyError:
            raise H5IOError(errno.ENOENT, 'No such Dataset or Group', path)
        return h5entry

    @staticmethod
    def get_name(h5entry):
        '''Return the entry file name in the fs as string of the hdf5 entry'''
        # XXX unicode does not seem to be allowed
        return str(osp.basename(h5entry.name))

    @staticmethod
    def get_size(h5entry):
        '''Return the byte size of the file'''
        raise NotImplementedError

    @staticmethod
    def get_data(h5entry, start, end):
        '''Return a slice of data from start to end'''
        raise NotImplementedError

    def get_stat(self, h5entry):
        '''Return the entry stat information (an instance of Stat)'''
        if isinstance(h5entry, h5py.highlevel.Group):
            return GroupStat()
        if isinstance(h5entry, h5py.highlevel.Dataset):
            return DatasetStat(st_size=self.get_size(h5entry))
        raise H5IOError(errno.ENOENT, 'Unknown entry type', h5entry.name)

    def list_group(self, group, specs=('.', '..')):
        '''A fonction generator that yields name of the entries in the group.
        The list is in arbitrary order with special entries ``specs``.
        This names are used as file/folder names
        '''
        return chain(iter(specs), imap(self.get_name, group.itervalues()))

    @staticmethod
    def openable(h5entry):
        '''raise H5IOError if not h5entry could not be readable'''
        if not isinstance(h5entry, h5py.highlevel.Dataset):
            raise H5IOError(errno.EISDIR, 'Is a Group', h5entry.name)

# ===

    def readdir(self, path, offset):
        '''Return a generator that yields entries from the given Group path
        used as file/folder contained in path'''
        convert = partial(fuse.Direntry, offset=offset)
        return imap(convert, self.list_group(self.get_entry(path)))

    def getattr(self, path):
        '''Return the stat attributes of the given ``path``'''
        return self.get_stat(self.get_entry(path))

    def open(self, path, flags):
        '''Raise H%IOError if no open is not allowed.

        XXX: readonly for now
        '''
        if (flags & os.O_RDONLY) != os.O_RDONLY:
            raise H5IOError(errno.EACCES, 'Could not open', path)
        return self.openable(self.get_entry(path))

    def read(self, path, size, offset):
        h5entry = self.get_entry(path)
        if isinstance(h5entry, h5py.highlevel.Group):
            raise H5IOError(errno.EISDIR, 'Is a Group', path)
        return self.get_data(h5entry, offset, offset + size)
