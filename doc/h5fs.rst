.. use /usr/bin/rst2man (docutils) to build the manpage

======
 H5FS
======


------------------------------------------------
mounts an HDF5 resource as a regular file system
------------------------------------------------

:Author: H5FS has been written by Alain Leufroy <contact@logilab.fr>
:Date:   2013-03-30
:Copyright: LGPL-v3
:Version: 0.1
:Manual section: 1
:Manual group: HDF5 Filesystem


SYNOPSIS
========

  mounting
    h5fs file mountpoint [options]

  unmounting
    fuserumount -u mountpoint


DESCRIPTION
===========

H5FS (Hierarchical Data Format FileSystem) is a file system for Linux (and other
operating systems with a FUSE implementation, such as Mac OS X or FreeBSD)
capable of operations on an HDF5 file.

On the local computer where the HDF5 file is mounted, the implementation makes
use of the FUSE (Filesystem in Userspace) kernel module. The practical effect of
this is that the end user can interact with the content of a HDF5 file in a
natural way as HDF5 uses a filesystem-like data format to access the resources.

GROUPS are exposed as folders and DATASETS are exposed as files.


OPTIONS
=======

General options:
----------------

--help, -h
  print help

--version, -v
  print version

--debug, -d
  start debug mode


EXAMPLES
========

This example shows how to mount an HDF5 file ``/path/to/file.h5`` to
``/tmp/mountpoint``::

% mkdir /tmp/mountpoint
% h5fs /path/to/file.h5 /tmp/mountpoint

The filesystem is now mounted and visible at ``/tmp/mountpoint``. Assuming that the
file contains a group "picture" with two datasets "image1" and "pallete", the
resources can be listed using the *tree* program:

::

  % tree /tmp/mountpoint
  /tmp/mountpoint
  `-- picture
      |-- image1.npy
      `-- pallete.npy
  
  1 directories, 2 files

The array of a dataset can be read using python and the numpy module:

::

  % python
  >>> import numpy
  >>> arr = numpy.load('/tmp/mountpoint/picture/image1.npy')
  >>> arr.shape
  (200, 400, 1)
  >>> exit()

To unmount the filesystem, use fusermount with the -u (unmount) option::

  % fusermount -u /tmp/mountpoint
  % rm -r /tmp/mountpoint


LIMITATIONS
===========

#. All features of HDF5 are not yet implemented (attributes, links)
#. Modifying resources are not yet implemented


SEE ALSO
========

* ``man fusermount``
* ``hdf5`` <http://www.hdfgroup.org>


DISCLAIMER
==========

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. Please refer to the "copyright" file distributed with H5FS
for complete details.
