#!/usr/bin/python3
import ctypes
import socket

from libnl import genl #pip3 install libnl
""" libnl Docs Source:
https://pypi.org/project/libnl/
https://github.com/Robpol86/libnl/blob/master/libnl/genl/family.py
"""


class Talker():

    def __init__(self):
        from pdb import set_trace
        set_trace()
        from libnl.genl.ctrl import genl_ctrl_resolve
        genl.genl_ctrl_resolve()


if __name__ == "__main__":
    Talker()