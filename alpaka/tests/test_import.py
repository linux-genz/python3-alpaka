#!/usr/bin/python3
import unittest
import os
import sys
from pdb import set_trace


class TestImports(unittest.TestCase):

    def test_import_all(self):
        try:
            import alpaka
            # Yes, manually call those objects. Do not tray automate/loop thorugh
            # the objects from the __init__, to make sure Nothing broke in case
            # of name changes and whatnot.
            alpaka.Messenger
            alpaka.Configurator
            alpaka.Alpaka
            self.assertTrue(True, 'Import successful.')
        except Exception as err:
            self.assertTrue(False, err)

if __name__ == '__main__':
    unittest.main()
