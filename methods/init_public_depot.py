#!/usr/bin/python3
# coding=utf-8

""" Route """

import os

from tools import web, log, repo_core  # pylint: disable=E0401


class Method:  # pylint: disable=E1101,R0903
    """ Method """

    # pylint: disable=W0201,R0912
    @web.init()
    def public_depot_init(self):
        """ Init """
        self.public_depot_groups = {}
        #
        repo_core_settings = repo_core.get_settings()
        #
        base_path = repo_core_settings.get("base_path", "/data/repo")
        depot_path = os.path.join(base_path, "public", "depot")
        #
        if not os.path.exists(depot_path):
            os.makedirs(depot_path)
        #
        log.info("Collecting public depot info")
        #
        for group_name in os.listdir(depot_path):
            plugins_path = os.path.join(depot_path, group_name, "plugins")
            bundles_path = os.path.join(depot_path, group_name, "bundles")
            #
            self.public_depot_groups[group_name] = {
                "plugins": self.collect_depot_group_plugins(plugins_path),
                "bundles": self.collect_depot_group_bundles(bundles_path),
            }
