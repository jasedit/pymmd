#!python
# -*- coding: utf-8 -*-

import unittest
import textwrap

import pymmd

class TestLoading(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(pymmd.valid_mmd())
    def test_version(self):

        version = pymmd.version()
        self.assertTrue(version)
        major, minor, patch = [int(ii) for ii in version.split('.', 3)]
        self.assertGreaterEqual(major, 5)
        if major >= 5:
            self.assertGreaterEqual(minor, 4)
            if minor >= 4:
                self.assertGreaterEqual(patch, 0)

    def test_metadata(self):
        base_txt = textwrap.dedent("""\
        title: Test
        author: Me

        # Introduction

        Here is some text.
        """)

        self.assertTrue(pymmd.has_metadata(base_txt, pymmd.COMPLETE))
        self.assertEqual(pymmd.extract_metadata_keys(base_txt), ['title', 'author'])
        self.assertEqual(pymmd.extract_metadata_value(base_txt, 'title'), 'Test')
        self.assertEqual(pymmd.extract_metadata_value(base_txt, 'author'), 'Me')

if __name__ == '__main__':
    unittest.main()
