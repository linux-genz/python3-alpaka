#!/usr/bin/python3
import unittest
import os
import sys
from pdb import set_trace

import alpaka


class TestMsngr(unittest.TestCase):

    def test_init(self):
        try:
            alpaka.Alpaka(async_cache=False)
        except Exception as err:
            self.assertTrue(False, err)


if __name__ == '__main__':
    unittest.main()
