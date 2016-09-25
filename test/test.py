#!python
# -*- coding: utf-8 -*-
"""Unit testing for pymmd"""

import unittest
import textwrap

import pymmd

class TestBasicMMD(unittest.TestCase):
    """Test Basic MMD operations."""
    def test_valid(self):
        """Test that pymmd loads the MMD library."""
        self.assertTrue(pymmd.valid_mmd())

    def test_version(self):
        """Test MMD version is reported, and a relatively modern version."""
        version = pymmd.version()
        self.assertTrue(version)
        major, minor, patch = [int(ii) for ii in version.split('.', 3)]
        self.assertGreaterEqual(major, 5)
        if major >= 5:
            self.assertGreaterEqual(minor, 4)
            if minor >= 4:
                self.assertGreaterEqual(patch, 0)

    def test_metadata(self):
        """Test basic metadata parsing."""
        base_txt = textwrap.dedent("""\
        title: Test
        author: Me

        # Introduction

        Here is some text.
        """)

        self.assertTrue(pymmd.has_metadata(base_txt, pymmd.COMPLETE))
        self.assertEqual(pymmd.keys(base_txt), ['title', 'author'])
        self.assertEqual(pymmd.value(base_txt, 'title'), 'Test')
        self.assertEqual(pymmd.value(base_txt, 'author'), 'Me')

    def text_empty_metadata(self):
        """Test metadata functions when metadata doesn't exist."""
        base_txt = textwrap.dedent("""\
          # Introduction

          Here is some text.
          """)

        self.assertFalse(pymmd.has_metadata(base_txt, pymmd.COMPLETE))
        self.assertEqual(pymmd.keys(base_txt), [])
        self.assertEqual(pymmd.value(base_txt, 'title'), '')

if __name__ == '__main__':
    unittest.main()
