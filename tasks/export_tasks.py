#!/usr/bin/python3
# coding=utf-8

""" Task """

import os
import gc
import random
import string

from tools import log, repo_core, this  # pylint: disable=E0401
from pylon.core.tools import process  # pylint: disable=E0401


def export_release_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    release_tag = kwargs["param"]
    #
    if not release_tag:
        log.error("Release not specified")
        return
    #
    log.info("Target: %s", release_tag)
    #
    export_release_tag = "export"
    #
    config = repo_core.get_settings()
    #
    base_path = config.get("base_path", "/data/repo")
    depot_path = os.path.join(base_path, "depot")
    #
    plugins_path = os.path.join(depot_path, export_release_tag, "plugins")
    bundles_path = os.path.join(depot_path, export_release_tag, "bundles")
    #
    if not os.path.exists(plugins_path):
        os.makedirs(plugins_path)
    #
    if not os.path.exists(bundles_path):
        os.makedirs(bundles_path)
    #
    log.info("Making archive")
    #
    base_name = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
    result_name = f"{base_name}.tar.gz"
    #
    target_path = os.path.join(bundles_path, result_name)
    #
    process.run_command(
        [
            "tar", "czvf", target_path,
            f"depot/{release_tag}/",
            f"simple/{release_tag}/",
            f"public/depot/{release_tag}/",
            f"public/simple/{release_tag}/",
        ],
        cwd=base_path,
    )
    #
    log.info("Updating registry")
    #
    group_data = {
        "plugins": this.module.collect_depot_group_plugins(plugins_path),
        "bundles": this.module.collect_depot_group_bundles(bundles_path),
    }
    #
    with this.module.lock:
        this.module.depot_groups[export_release_tag] = group_data
        this.descriptor.save_state()
    #
    log.info("Result: %s", result_name)
    #
    gc.collect()


def remove_export_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    export_file = kwargs["param"]
    #
    if not export_file:
        log.error("Export file not specified")
        return
    #
    log.info("Target: %s", export_file)
    #
    export_release_tag = "export"
    #
    config = repo_core.get_settings()
    #
    base_path = config.get("base_path", "/data/repo")
    depot_path = os.path.join(base_path, "depot")
    #
    plugins_path = os.path.join(depot_path, export_release_tag, "plugins")
    bundles_path = os.path.join(depot_path, export_release_tag, "bundles")
    #
    if not os.path.exists(plugins_path):
        os.makedirs(plugins_path)
    #
    if not os.path.exists(bundles_path):
        os.makedirs(bundles_path)
    #
    log.info("Deleting archive")
    #
    target_path = os.path.join(bundles_path, export_file)
    #
    if os.path.exists(target_path):
        os.remove(target_path)
    #
    log.info("Updating registry")
    #
    group_data = {
        "plugins": this.module.collect_depot_group_plugins(plugins_path),
        "bundles": this.module.collect_depot_group_bundles(bundles_path),
    }
    #
    with this.module.lock:
        this.module.depot_groups[export_release_tag] = group_data
        this.descriptor.save_state()
    #
    gc.collect()
