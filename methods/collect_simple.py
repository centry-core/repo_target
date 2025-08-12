#!/usr/bin/python3
# coding=utf-8

""" Route """

import re
import os
import time
import hashlib

import pkginfo  # pylint: disable=E0401

from tools import web  # pylint: disable=E0401


class Method:  # pylint: disable=E1101,R0903
    """ Method """

    # pylint: disable=W0201,R0912
    @web.method()
    def collect_simple_group_wheels(self, wheel_path):
        """ Method """
        result = {}
        #
        if os.path.exists(wheel_path):
            for file_name in os.listdir(wheel_path):
                time.sleep(0.01)  # yield
                #
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
                if wheel_name not in result:
                    result[wheel_name] = {}
                #
                result[wheel_name][file_name] = {
                    "file": file_path,
                    "size": os.path.getsize(file_path),
                    "hashes": {
                        "sha256": file_digest.hexdigest(),
                    },
                    "metadata_hashes": {
                        "sha256": hashlib.sha256(wheel_metadata).hexdigest(),
                    },
                    "metadata": wheel_metadata.decode(),
                    "version": wheel.version,
                    "requires_python": wheel_requires_python,
                }
        #
        return result
