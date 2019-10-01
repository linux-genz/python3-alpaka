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

# Get on the Generic bus.  Uses the llamas test module.

# https://docs.pyroute2.org/ for info, but the source is best, especially
# /usr/lib/python3/dist-packages/pyroute2/netlink/generic/__init__.py
import errno
import os
import socket
import sys
import time
import uuid
import logging

from pdb import set_trace
from pprint import pprint
from types import SimpleNamespace

from pyroute2.common import map_namespace
from pyroute2.netlink import NETLINK_GENERIC, NetlinkError
from pyroute2.netlink import NLM_F_REQUEST, NLM_F_DUMP, NLM_F_ACK
from pyroute2.netlink import nla, nla_base, genlmsg
from pyroute2.netlink.generic import GenericNetlinkSocket
from pyroute2.netlink.nlsocket import Marshal

from .configurator import Configurator
# Used in kernel module: genl_register_family(struct genl_family.name).
# After insmod, run "genl -d ctrl  list" and eventually see
# Name: genz_cmd
#       ID: 0x18  Version: 0x1  header size: 0  max attribs: 3
#       commands supported:
#               #1:  ID-0x0
#               #2:  ID-0x1
#               #3:  ID-0x2
#
# ID == 0x18 (== 24) is dynamic and only valid in this scenario, and I've
# seen the 24 in embedded structures.  Version in kernel == 1, no header,
# max 3 attribs == fields in 'MsgProps': gcid, cclass, uuid (user_send.c).

# GENZ_GENL_FAMILY_NAME   = 'genz_cmd'
# GENZ_GENL_VERSION       = 1

# Commands are matched from kern_recv.c::struct genl_ops genz_gnl_ops.
# Kernel convention is not to use zero as an index or base value.

GENZ_C_PREFIX            = 'GENZ_C_'

GENZ_C_ADD_COMPONENT     = 1    # from genz_genl.h "enum"
GENZ_C_REMOVE_COMPONENT  = 2
GENZ_C_SYMLINK_COMPONENT = 3

# Coalesce the commands into a forward and reverse map.
# From https://www.open-mesh.org/attachments/857/neighbor_extend_dump.py

(GENZ_C_name2num, GENZ_C_num2name) = map_namespace(GENZ_C_PREFIX, globals())
# These mixins are given to pyroute2 to build packed structs for sending to
# C routines (libnl).  They're just linked lookup tables whose attributes are
# proscribed by internals.  The choices for encoding (uint32, asciiz, etc)
# are each a class in netlink/__init.__.py "class nlmsg_atoms".  If you
# don't like those choices, add a class here then add it as a new class
# attribute to nlmsg.  Only override __init__ for a set_trace, nothing else.
# See also netlink/__init__.py::register_nlas() for optional fields.


class KernelMsgModel(genlmsg):
    """
        The set of all Netlink Attributes (NLAs) that could be passed.
    This is the analog of the kernel "struct nla_policy".
    """
    prefix = 'GENZ_A_'      # A for "Attribute", a convenice for me.

    # Zero-based arrays are sort-of needed here, but also somewhat frowned
    # upon. This needs further research, maybe in pyroute2 itself.
    nla_map = None


class Commandment(Marshal):
    """
        The set of all command numbers and their associated message structures.
    This is the analog of the kernel 'struct genl_ops'.
    """
    msg_map = {}


class Messenger(GenericNetlinkSocket):
    """
        Constructs a netlink message in the right format from the config file
    (default one should be in the root of the project) and sends the message to
    the destination.
    """

    def __init__(self, *args, **kwargs):
        """
            @param 'config' <str>: Path to a config file. Default: ./config
            @param 'msg_flags' <int>: Default: NLM_F_REQUEST|NLM_F_ACK. A pyrouter2
                                    flag used to send a message.
            @param 'dont_bind' <bool>: False or None - self.bind is called.
                                    True - user has to call self.bind manually.
        """
        super().__init__(*args, **kwargs)

        cfg_path = kwargs.get('config', None)
        if cfg_path is None:
            cfg_path = os.path.abspath(os.path.realpath(__file__))
            cfg_path = os.path.dirname(cfg_path)
            cfg_path = os.path.join(cfg_path, 'config')
            logging.warning('ZooKeeper received no config. Using default at: %s' % cfg_path)
            # raise RuntimeError('Missing "config" argument!')

        assert(os.path.exists(cfg_path)), 'Config at %s not found!' % cfg_path

        self.msg_flags = kwargs.get('msg_flags', NLM_F_REQUEST|NLM_F_ACK)
        self.cmd = Commandment()    # Now pyroute2 methods see it.
        self.cfg = Configurator(cfg_path)


    @property
    def runtime_id(self):
        """ ID for this instance that will be used when binding to the kernel. """
        return os.getpid()


    def _clean_kwargs(self, keys: list, kwargs: dict)  -> dict:
        """
            GenericNetlinkSocket __init__ doesn't like any
        """
        for k in keys:
            if k in kwargs:
                del kwargs[k]
        return kwargs


    def _assign_msg_to_cmd(self, cfg_model: dict):
        """
            Set the Message Model per each Command type when it is None.
        """
        model = cfg_model
        for key in model.keys():
            if model[key] is None:
                model[key] = self.msg_model
        return model


    def bind(self, **kwargs):
        """Exposed here instead of just automatically doing it."""
        try:
            super().bind(
                self.cfg.family_name,
                self.msg_model,
                groups=0,
                pid=self.runtime_id,
                **kwargs)
            return          # self.prid is now set, BTW
        except NetlinkError as exc:
            self.close()
            if exc.code == errno.ENOENT:
                raise RuntimeError(
                    'No kernel response for "%s"' % self.cfg.family_name)
            raise(exc)
        except Exception as exc:
            self.close()
            raise RuntimeError('bind() failed: %s' % str(exc))


    def build_msg(self, cmd, **kwargs):
        # pyroute2 expacts a certain class and format for the "message" protocols.
        # This sets everything needed from the config file.
        self.msg_model = KernelMsgModel
        self.msg_model.nla_map = self.cfg.get_msg_model(cmd)
        self.cmd.msg_map = self.cfg.cmd_model

        # construct a Command Model for the netlink communication
        self.cfg.cmd_model = self._assign_msg_to_cmd(self.cfg.cmd_model)

        if not kwargs.get('dont_bind', False):
            self.bind()


    def sendmsg(self, msg):
        return self.nlm_request(msg,
                                msg_type=self.prid,
                                msg_flags=NLM_F_REQUEST|NLM_F_ACK)