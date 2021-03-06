"""
<Program Name>
  test_storage.py

<Author>
  Joshua Lock <jlock@vmware.com>

<Started>
  April 17, 2020

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Unit test for 'storage.py'
"""

# Help with Python 3 compatibility, where the print statement is a function, an
# implicit relative import is invalid, and the '/' operator performs true
# division.  Example:  print 'hello world' raises a 'SyntaxError' exception.
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os
import tempfile
import unittest

import securesystemslib.exceptions
import securesystemslib.storage

import six


class TestStorage(unittest.TestCase):
  def setUp(self):
    self.storage_backend = securesystemslib.storage.FilesystemBackend()
    self.temp_dir = tempfile.mkdtemp(dir=os.getcwd())
    self.filepath = os.path.join(self.temp_dir, 'testfile')
    with open(self.filepath, 'wb') as test:
        test.write(b'testing')
    self.fileobj = open(self.filepath, 'rb')


  def tearDown(self):
    self.fileobj.close()


  def test_exceptions(self):
    try:
      with self.storage_backend.get('/none/existent/path') as file_object:
        file_object.read()
    except Exception as exc:
      self.assertIsInstance(exc, securesystemslib.exceptions.StorageError)

    self.assertRaises(securesystemslib.exceptions.StorageError,
        self.storage_backend.put, self.fileobj, '/none/existent/path')

    self.assertRaises(securesystemslib.exceptions.StorageError,
        self.storage_backend.getsize, '/none/existent/path')

    self.assertRaises(securesystemslib.exceptions.StorageError,
        self.storage_backend.create_folder, '/none/existent/path')

    self.assertRaises(securesystemslib.exceptions.StorageError,
        self.storage_backend.list_folder, '/none/existent/path')


  def test_files(self):
    with self.storage_backend.get(self.filepath) as get_fileobj:
      self.assertEqual(get_fileobj.read(), self.fileobj.read())

    self.assertEqual(self.storage_backend.getsize(self.filepath),
        os.path.getsize(self.filepath))

    put_path = os.path.join(self.temp_dir, 'put')
    with self.storage_backend.get(self.filepath) as get_fileobj:
      self.storage_backend.put(get_fileobj, put_path)
      self.fileobj.seek(0)
      with open(put_path, 'rb') as put_file:
        self.assertEqual(put_file.read(), self.fileobj.read())

    self.assertTrue(os.path.exists(put_path))
    self.storage_backend.remove(put_path)
    self.assertFalse(os.path.exists(put_path))


  def test_folders(self):
    leaves = ['test1', 'test2', 'test3']
    folder = os.path.join(self.temp_dir, 'test_dir')
    self.storage_backend.create_folder(folder)
    for leaf in leaves:
      with open(os.path.join(folder, leaf), 'wb') as fi:
        fi.write(leaf.encode('utf-8'))
    found_leaves = self.storage_backend.list_folder(folder)
    self.assertListEqual(leaves, sorted(found_leaves))

    # Test trying to create a folder with an empty string
    self.storage_backend.create_folder('')
