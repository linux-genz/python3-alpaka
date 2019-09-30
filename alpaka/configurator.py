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


    @property
    def version(self) -> int:
        return self.get('VERSION', 1)

    @property
    def family_name(self) -> str:
        return self.get('NETLINK_FAMILY_NAME', None)

    @property
    def msg_model(self) -> tuple:
        return self.cfg['MSG_MODEL']

    @property
    def cmd_opts(self) -> dict:
        return self.cfg['CMD_OPTS']

    @property
    def cmd_model(self) -> dict:
        return self.get('CMD_MODEL', None)

    @cmd_model.setter
    def cmd_model(self, value):
        if not isinstance(value, dict):
            msg = 'Unexpected value type when cetting cmd_model! '
            msg += 'Expected <dict> but %s has arrived!' % type(value)
            logging.error(msg)
            return

        self.cfg['CMD_MODEL'] = value