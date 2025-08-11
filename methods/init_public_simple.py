#!/usr/bin/python3
# coding=utf-8

""" Route """

import re
import os
import hashlib

import pkginfo  # pylint: disable=E0401

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
            self.public_simple_groups[group_name] = {}
            #
            wheel_path = os.path.join(group_path, group_name)
            #
            if os.path.exists(wheel_path):
                for file_name in os.listdir(wheel_path):
                    file_path = os.path.join(wheel_path, file_name)
                    #
                    with open(file_path, "rb") as file:
                        file_digest = hashlib.file_digest(file, "sha256")
                    #
                    wheel = pkginfo.Wheel(file_path)
                    wheel_name = re.sub(r"[-_.]+", "-", wheel.name).lower()
                    wheel_metadata = wheel.read()
                    #
                    try:
                        wheel_requires_python = wheel.requires_python
                    except:  # pylint: disable=W0702
                        wheel_requires_python = None
                    #
                    if wheel_name not in self.public_simple_groups[group_name]:
                        self.public_simple_groups[group_name][wheel_name] = {}
                    #
                    self.public_simple_groups[group_name][wheel_name][file_name] = {
                        "file": file_path,
                        "size": os.path.getsize(file_path),
                        "hashes": {
                            "sha256": file_digest.hexdigest(),
                        },
                        "metadata_hashes": {
                            "sha256": hashlib.sha256(wheel_metadata).hexdigest(),
                        },
                        "metadata": wheel_metadata,
                        "version": wheel.version,
                        "requires_python": wheel_requires_python,
                    }
