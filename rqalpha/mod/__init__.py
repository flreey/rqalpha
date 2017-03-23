# -*- coding: utf-8 -*-
#
# Copyright 2017 Ricequant, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from importlib import import_module
from collections import OrderedDict

from rqalpha.utils.logger import system_log
from rqalpha.utils.i18n import gettext as _
from rqalpha.utils import RqAttrDict


class ModHandler(object):
    def __init__(self):
        self._env = None
        self._mod_list = list()
        self._mod_dict = OrderedDict()

    def set_env(self, environment):
        self._env = environment

        config = environment.config

        for mod_name in config.mod.__dict__:
            mod_config = getattr(config.mod, mod_name)
            if not mod_config.enabled:
                continue
            if not hasattr(mod_config, "priority"):
                setattr(mod_config, "priority", 100)
            self._mod_list.append((mod_name, mod_config))

        self._mod_list.sort(key=lambda item: item[1].priority)
        for idx, (mod_name, user_mod_config) in enumerate(self._mod_list):
            if mod_name in SYSTEM_MOD_LIST:
                lib_name = "rqalpha.mod.rqalpha_mod_" + mod_name
            system_log.debug(_('loading mod {}').format(lib_name))
            mod_module = import_module(lib_name)
            mod = mod_module.load_mod()

            mod_config = RqAttrDict(getattr(mod_module, "__config__", {}))
            mod_config.update(user_mod_config)
            print((mod_name, user_mod_config), mod_config)
            self._mod_list[idx] = (mod_name, mod_config)
            self._mod_dict[mod_name] = mod

        environment.mod_dict = self._mod_dict

    def start_up(self):
        for mod_name, mod_config in self._mod_list:
            self._mod_dict[mod_name].start_up(self._env, mod_config)

    def tear_down(self, *args):
        for mod_name, __ in reversed(self._mod_list):
            self._mod_dict[mod_name].tear_down(*args)

SYSTEM_MOD_LIST = [
    "sys_analyser",
    "sys_funcat",
    "sys_risk",
    "sys_simulation",
    "sys_stock_realtime",
]
