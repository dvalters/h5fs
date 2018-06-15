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

import os
import os.path as osp
import tempfile
import errno
import h5py
import numpy as N
from StringIO import StringIO

from unittest2 import TestCase as TC, main
from logilab.common.testlib import within_tempdir

import h5fs
FSM = h5fs.FsMixin()

__folder__=osp.dirname(osp.abspath(__file__))

def getdata(path):
    return osp.join(__folder__, 'data', path)

def with_h5file(func):
    @within_tempdir
    def wrapped(self):
        h5file = h5py.File('file.hdf5')
        out = func(self, h5file)
        h5file.close()
        return out
    return wrapped


def with_mixin(clsmixin):
    def wrapper(func):
        @with_h5file
        def wrapped(self, h5file):
            h5file.create_group(u'sam')
            data = N.array([(-1, 4.0, 'Hello'), (2, 6.0, 'World')],
                           dtype=[('f0', '>u8'), ('f1', '>f4'), ('f2', '|S7')])
            h5file.create_dataset(u'melu', data=data)
                # data=xrange(12), shape=(4, 3), dtype='u4')
            fsmx = clsmixin()
            fsmx.h5file = h5file
            return func(self, fsmx)
        return wrapped
    return wrapper


class FsMixin_TC(TC):
    @with_mixin(h5fs.FsMixin)
    def test_get_dataset_size(self, fsmx):
        self.assertEqual(fsmx.get_size(fsmx.h5file['melu']), 38)

    @with_mixin(h5fs.FsMixin)
    def test_get_stat_with_group(self, fsmx):
        group = fsmx.h5file['sam']
        self.assertTrue(isinstance(fsmx.get_stat(group), h5fs.GroupStat))

    @with_mixin(h5fs.FsMixin)
    def test_get_stat_with_dataset(self, fsmx):
        dataset = fsmx.h5file['melu']
        stat = fsmx.get_stat(dataset)
        self.assertTrue(isinstance(stat, h5fs.DatasetStat))
        self.assertEqual(stat.st_size, 38)

    @with_mixin(h5fs.FsMixin)
    def test_get_name(self, fsmx):
        dataset = fsmx.h5file['melu']
        self.assertEqual(fsmx.get_name(dataset), 'melu')

    @with_mixin(h5fs.FsMixin)
    def test_get_data(self, fsmx):
        self.assertSequenceEqual(fsmx.get_data(fsmx.h5file['melu'], 7, 19),
                                 '\xff@\x80\x00\x00Hello\x00\x00')

    @with_mixin(h5fs.FsMixin)
    def test_list_group(self, fsmx):
        result = set(fsmx.list_group(fsmx.h5file['/'], ('alain',)))
        self.assertSetEqual(result, set(['sam', 'melu', 'alain']))

    @with_mixin(h5fs.FsMixin)
    def test_openable_wrong(self, fsmx):
        self.assertRaises(h5fs.H5IOError, fsmx.openable, fsmx.h5file['sam'])

    @with_mixin(h5fs.FsMixin)
    def test_openable_ok(self, fsmx):
        fsmx.openable(fsmx.h5file['melu']) # no H5IOError raised

# =======

    @with_mixin(h5fs.FsMixin)
    def test_readdir(self, fsmx):
        result = list(fsmx.readdir(u'/', 0))
        expected = list(fsmx.h5file[u'/'].keys()) + ['.', '..']
        self.assertEqual(len(expected), len(result))

    @with_mixin(h5fs.FsMixin)
    def test_readdir_wrong(self, fsmx):
        self.assertRaises(h5fs.H5IOError, fsmx.readdir, u'/wrong data path', 0)

    @with_mixin(h5fs.FsMixin)
    def test_getattr(self, fsmx):
        self.assertTrue(isinstance(fsmx.getattr('/'), h5fs.GroupStat))
        self.assertTrue(isinstance(fsmx.getattr('/sam'), h5fs.GroupStat))
        self.assertTrue(isinstance(fsmx.getattr('/melu'), h5fs.DatasetStat))

    @with_mixin(h5fs.FsMixin)
    def test_getattr_wrong(self, fsmx):
        self.assertRaises(h5fs.H5IOError, fsmx.getattr, u'/wrong data path')

    @with_mixin(h5fs.FsMixin)
    def test_open_wrong_path(self, fsmx):
        self.assertRaises(h5fs.H5IOError, fsmx.open, u'/wrong data path',
                          os.O_RDONLY)

    @with_mixin(h5fs.FsMixin)
    def test_open_wrong_write(self, fsmx): # XXX read-only for now
        self.assertRaises(h5fs.H5IOError, fsmx.open, u'/wrong data path',
                          os.O_WRONLY)

    @with_mixin(h5fs.FsMixin)
    def test_open_ok(self, fsmx):
        fsmx.open(u'melu', os.O_RDONLY) # no H5IOError raised

    @with_mixin(h5fs.FsMixin)
    def test_read_wrong_noent(self, fsmx):
        self.assertRaises(h5fs.H5IOError, fsmx.read, u'/wrong data path', 0, 10)

    @with_mixin(h5fs.FsMixin)
    def test_read_wrong_isdir(self, fsmx):
        self.assertRaises(h5fs.H5IOError, fsmx.read, u'/sam', 0, 10)

    @with_mixin(h5fs.FsMixin)
    def test_read(self, fsmx):
        self.assertSequenceEqual(fsmx.read(u'melu', 12, 7),
                                 '\xff@\x80\x00\x00Hello\x00\x00')


class Npy10FsMixin_TC(TC):
    @with_mixin(h5fs.Npy10FsMixin)
    def test_get_dataset_npy_header(self, mx):
        dataset = mx.h5file['melu']
        reference = StringIO()
        N.lib.format.write_array(reference, dataset.value, version=(1,0))
        reference.seek(0)
        header_ref = ''.join(iter(lambda: reference.read(1), '\n')) + '\n'
        value = mx._get_npy_header(dataset)
        self.assertMultiLineEqual(header_ref, value)

    @with_mixin(h5fs.Npy10FsMixin)
    def test_get_dataset_size(self, mx):
        dataset = mx.h5file['melu']
        reference = StringIO()
        N.lib.format.write_array(reference, dataset.value, version=(1,0))
        reference.seek(0)
        len_ref = len(reference.getvalue())
        self.assertEqual(mx.get_size(dataset), len_ref)

    @with_mixin(h5fs.Npy10FsMixin)
    def test_get_data(self, mx):
        self.assertMultiLineEqual(mx.get_data(mx.h5file['melu'], 10, 20),
                                  "{'descr': ")
        self.assertMultiLineEqual(mx.get_data(mx.h5file['melu'], 119, 131),
                                  '\xff@\x80\x00\x00Hello\x00\x00')
        self.assertMultiLineEqual(
            mx.get_data(mx.h5file['melu'], 100, 128),
            '(2,), }    \n\xff\xff\xff\xff\xff\xff\xff\xff@\x80\x00\x00Hell')

    @with_mixin(h5fs.Npy10FsMixin)
    def test_get_dataset_name(self, mx):
        dataset = mx.h5file['melu']
        self.assertEqual(mx.get_name(dataset), 'melu.npy')

    @with_mixin(h5fs.Npy10FsMixin)
    def test_get_group_name(self, mx):
        dataset = mx.h5file['sam']
        self.assertEqual(mx.get_name(dataset), 'sam')

    @with_mixin(h5fs.Npy10FsMixin)
    def test_get_dataset_entry(self, mx):
        dataset = mx.h5file['melu']
        self.assertEqual(mx.get_entry('melu.npy'), dataset)

    @with_mixin(h5fs.Npy10FsMixin)
    def test_get_group_entry(self, mx):
        dataset = mx.h5file['sam']
        self.assertEqual(mx.get_entry('sam'), dataset)


if __name__ == '__main__':
    main()
