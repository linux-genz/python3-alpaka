#!/usr/bin/python3
from flask import Flask
import os
import logging


class Configurator():

    def __init__(self, cfg_path):
        self.cfg = self._read_config(cfg_path)

    def _read_config(self, path):
        if not os.path.exists(path):
            raise RuntimeError('No pyconfig file at %s' % path)

        flask_obj = Flask('flask_for_cfg_parsing')
        flask_obj.config.from_pyfile(path)
        return flask_obj.config


    def get(self, key, default=None):
        if self.cfg is None:
            logging.warning('Alpaka config is None while getting a key "%s"' % key)
            return None

        return self.cfg.get(key, default)


    def get_msg_model(self, cmd) -> tuple:
        """
         Exctract a message model extracted from config's CMD_MODEL property.
        (It is probably will be assigned to the KernelMsgModel.nla_map somewhere)

        @param cmd: <int or str> model name to extract from CMD_MODEL. For int
                    value, model will be extracted directly from CMD_MODEL.
                    For Str value, it will look up CMD_OPTS for that index.

        @return: a model defined for the cmd in the config for the CMD_MODEL.
        """

        #Extracting a correlated Index from the CMD_OPTS for the str cmd
        if isinstance(cmd, str):
            if cmd not in self.cmd_opts:
                msg = 'get_msg_model() -> cmd=%s not in cmd_opts: %s'
                msg = msg % (cmd, list(self.cmd_opts.keys))
                logging.warning(msg)
            else:
                cmd = self.cmd_opts.get(cmd)
        #cmd is an int - so look up CMD_MODEL directly
        elif cmd not in self.cmd_model:
            msg = 'get_msg_model() -> cmd=%s not found in CMD_MODEL keys: %s'
            msg = msg % (cmd, list(self.cmd_model.keys()))
            logging.warning(msg)

        return self.cmd_model.get(cmd, None)


    @property
    def version(self) -> int:
        return self.get('VERSION', 1)


    @property
    def family_name(self) -> str:
        return self.get('NETLINK_FAMILY_NAME', None)


    @property
    def cmd_opts(self) -> dict:
        return self.cfg['CMD_OPTS']


    @property
    def cmd_model(self) -> dict:
        return self.get('CMD_MODEL', None)


    @cmd_model.setter
    def cmd_model(self, value: tuple):
        self.cfg['CMD_MODEL'] = value