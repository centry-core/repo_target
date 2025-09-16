#!/usr/bin/python3
# coding=utf-8
# pylint: disable=C0411

""" Method """

# pylint: disable=E0401
from tools import web


class Method:  # pylint: disable=E1101,R0903
    """ Method """

    # pylint: disable=W0201,R0912
    @web.method()
    def get_pip_args(self, config, release_tag, file_name):
        """ Method """
        pip_cfg = config.get("pip_args", {})
        #
        common_cfg = pip_cfg.get("common", [])
        per_release_cfg = pip_cfg.get("per_release", {})
        per_plugin_cfg = pip_cfg.get("per_plugin", {})
        #
        if file_name in per_plugin_cfg:
            return per_plugin_cfg[file_name]
        #
        if release_tag in per_release_cfg:
            return per_release_cfg[release_tag]
        #
        return common_cfg
