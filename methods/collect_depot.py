#!/usr/bin/python3
# coding=utf-8

""" Route """

import os
import json
import tarfile

from tools import web  # pylint: disable=E0401


class Method:  # pylint: disable=E1101,R0903
    """ Method """

    # pylint: disable=W0201,R0912
    @web.method()
    def collect_depot_group_plugins(self, plugins_path):
        """ Method """
        result = {}
        #
        if os.path.exists(plugins_path):
            for file_name in os.listdir(plugins_path):
                if not file_name.endswith(".tar.gz"):
                    continue
                #
                file_path = os.path.join(plugins_path, file_name)
                #
                plugin_name = file_name.rsplit(".", 2)[0]
                plugin_metadata = None
                plugin_requirements = None
                #
                with tarfile.open(file_path) as file:
                    while member := file.next():
                        member_name = member.name
                        #
                        if "/" not in member_name:
                            continue
                        #
                        member_name = member_name.split("/", 1)[1]
                        #
                        if member_name == "metadata.json":
                            try:
                                plugin_metadata = json.loads(
                                    file.extractfile(member).read()
                                )
                            except:  # pylint: disable=W0702
                                pass
                        #
                        if member_name == "requirements.txt":
                            try:
                                plugin_requirements = file.extractfile(member).read()
                            except:  # pylint: disable=W0702
                                pass
                        #
                        if plugin_metadata is not None and plugin_requirements is not None:
                            break
                #
                if plugin_metadata is None:
                    continue
                #
                if plugin_requirements is None:
                    plugin_requirements = b""
                #
                result[plugin_name] = {
                    "file": file_path,
                    "size": os.path.getsize(file_path),
                    "metadata": plugin_metadata,
                    "requirements": plugin_requirements,
                }
        #
        return result

    # pylint: disable=W0201,R0912
    @web.method()
    def collect_depot_group_bundles(self, bundles_path):
        """ Method """
        result = {}
        #
        if os.path.exists(bundles_path):
            for file_name in os.listdir(bundles_path):
                file_path = os.path.join(bundles_path, file_name)
                #
                result[file_name] = {
                    "file": file_path,
                    "size": os.path.getsize(file_path),
                }
        #
        return result
