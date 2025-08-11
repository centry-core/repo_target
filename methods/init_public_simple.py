#!/usr/bin/python3
# coding=utf-8

""" Route """

import os

from tools import web, log, repo_core  # pylint: disable=E0401


class Method:  # pylint: disable=E1101,R0903
    """ Method """

    # pylint: disable=W0201
    @web.init()
    def public_simple_init(self):
        """ Init """
        self.public_simple_groups = {}
        #
        repo_core_settings = repo_core.get_settings()
        #
        base_path = repo_core_settings.get("base_path", "/data/repo")
        group_path = os.path.join(base_path, "public", "simple")
        #
        if not os.path.exists(group_path):
            os.makedirs(group_path)
        #
        log.info("Collecting public wheel info")
        #
        for group_name in os.listdir(group_path):
            wheel_path = os.path.join(group_path, group_name)
            #
            self.public_simple_groups[group_name] = self.collect_simple_group_wheels(wheel_path)
