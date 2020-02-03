#!/usr/bin/python3
"""
 * (C) Copyright 2018 Hewlett Packard Enterprise Development LP”.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do
 * so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# Co-opt the pyroute2 NetlinkSocket (which defaults to GenericNetlinkSocket) to
# listen on the Netlink KOBJECT_UEVENT bus for module and device activity.
# modprobe/rmmod of the fee_bridge module shows lots of stuff.

# https://docs.pyroute2.org/ for info, but the source is best, especially
# /usr/lib/python3/dist-packages/pyroute2/netlink/nlsocket.py

import os
import socket
import sys
import time

from pdb import set_trace
from pprint import pprint
from types import SimpleNamespace

from pyroute2.netlink import NETLINK_KOBJECT_UEVENT
from pyroute2.netlink.nlsocket import NetlinkSocket     # RTFF


class Alpaka(NetlinkSocket):

    def __init__(self, *args, **kwargs):
        # NetlinkSocket has no __init__ so end up in nlsocket.py::NetlinkMixin.__init__
        # which is expecting family, port, pid, and fileno.  Its "post_init()" creates
        # self._sock (visible here).  It also provides accessor methods so I should
        # never hit self._sock directly.
        kwargs['family'] = kwargs.get('family', NETLINK_KOBJECT_UEVENT) # Override
        async_prop_name = 'async_cache'
        asyncval = bool(kwargs.get(async_prop_name, False))
        if async_prop_name in kwargs:
            del kwargs[async_prop_name]

        super().__init__(*args, **kwargs)
        self.bind(groups=-1, async_cache=asyncval)      # zero was a bad choice


    def _cooked(self, raw):
        elems = [ r for r in raw.split(b'\x00') ]
        elem0 = elems.pop(0).decode()
        if elem0 == 'libudev':
            retobj = SimpleNamespace(src='libudev')
            grunge = bytes()    # FIXME: grunge kernel src, decode this mess
            while not elems[0].startswith(b'ACTION='):
                grunge += elems.pop(0)
            retobj.header = grunge
        else:
            retobj = SimpleNamespace(src='kernel', header=elem0)
        # Should just be key=value left
        for e in elems:
            if e:
                key, value = e.decode().split('=')
                setattr(retobj, key.strip(), value.strip())
        return retobj


    def __call__(self):
        '''Returns None or an object based on blocking/timeout.'''
        try:
            raw = self.recv(4096)
        except BlockingIOError:  # EWOULDBLOCK
            return None
        return self._cooked(raw)


    @property
    def blocking(self):
        '''Per docs, True -> timeout == None, False -> timeount == 0.0'''
        to = self.gettimeout()
        return True if to is None else bool(to)


    @blocking.setter
    def blocking(self, newstate):
        '''Per docs, True -> timeout == None, False -> timeount == 0.0'''
        self.setblocking(bool(newstate))


    @property
    def timeout(self):
        return self.gettimeout()

    @timeout.setter
    def timeout(self, newto):
        '''newto must be None or float(>= 0.0)'''
        assert newto is None or float(newto) >= 0.0, 'bad timeout value'
        self.settimeout(newto)

    @property
    def timeout(self):
        return self.gettimeout()

    @property
    def rdlen(self):
        return self.buffer_queue.qsize()

    def dequeue(self, count=-1):
        retlist = []
        if count <= 0:
            while True:
                try:
                    retlist.append(
                        self._cooked(self.buffer_queue.get(block=False)))
                except Empty as err:
                    return retlist

        while count > 0:
            retlist.append(self._cooked(self.buffer_queue.get(block=True)))
            count -= 1
        return retlist

# Callback is hit only during kuns.get() which can hang.  The message it gets
# is crap; maybe the logic is more suited to (generic) netlink than the
# multiple udev notifiers?

if __name__ == '__main__':
    async_cache = len(sys.argv) > 1
    kuns = Alpaka(async_cache=async_cache)
    if async_cache:
        print('\nAsync reads...', end='')
        while True:
            while not kuns.rdlen:
                print('.', end='')
                sys.stdout.flush()
                time.sleep(1)
            print('\n', kuns.dequeue(count=1))

    print('\nBlocking reads...')
    kuns.blocking = True        # It's the default value; play with others.
    while True:
        try:
            val = kuns()
        except KeyboardInterrupt:
            print('\nExiting...')
            break
        if val is None:
            print('Nada')
        else:
            pprint(val)