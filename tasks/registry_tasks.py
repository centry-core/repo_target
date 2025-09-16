#!/usr/bin/python3
# coding=utf-8

""" Task """

import os
import gc
import shutil

from tools import log, repo_core, this  # pylint: disable=E0401


def sync_registry_task(*_args, **_kwargs):
    """ Task """
    repo_core_settings = repo_core.get_settings()
    base_path = repo_core_settings.get("base_path", "/data/repo")
    #
    # Public depot
    #
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
        group_data = {
            "plugins": this.module.collect_depot_group_plugins(plugins_path),
            "bundles": this.module.collect_depot_group_bundles(bundles_path),
        }
        #
        with this.module.lock:
            this.module.public_depot_groups[group_name] = group_data
            this.descriptor.save_state()
    #
    gc.collect()
    #
    # Public simple
    #
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
        group_data = this.module.collect_simple_group_wheels(wheel_path)
        #
        with this.module.lock:
            this.module.public_simple_groups[group_name] = group_data
            this.descriptor.save_state()
    #
    gc.collect()
    #
    # Depot
    #
    depot_path = os.path.join(base_path, "depot")
    #
    if not os.path.exists(depot_path):
        os.makedirs(depot_path)
    #
    log.info("Collecting depot info")
    #
    for group_name in os.listdir(depot_path):
        plugins_path = os.path.join(depot_path, group_name, "plugins")
        bundles_path = os.path.join(depot_path, group_name, "bundles")
        #
        group_data = {
            "plugins": this.module.collect_depot_group_plugins(plugins_path),
            "bundles": this.module.collect_depot_group_bundles(bundles_path),
        }
        #
        with this.module.lock:
            this.module.depot_groups[group_name] = group_data
            this.descriptor.save_state()
    #
    gc.collect()
    #
    # Simple
    #
    group_path = os.path.join(base_path, "simple")
    #
    if not os.path.exists(group_path):
        os.makedirs(group_path)
    #
    log.info("Collecting wheel info")
    #
    for group_name in os.listdir(group_path):
        wheel_path = os.path.join(group_path, group_name)
        #
        group_data = this.module.collect_simple_group_wheels(wheel_path)
        #
        with this.module.lock:
            this.module.simple_groups[group_name] = group_data
            this.descriptor.save_state()
    #
    gc.collect()


def purge_release_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    release_tag = kwargs["param"]
    #
    if not release_tag:
        log.error("Release not specified")
        return
    #
    log.info("Target: %s", release_tag)
    #
    log.info("Purging from state")
    with this.module.lock:
        this.module.public_depot_groups.pop(release_tag, None)
        this.module.public_simple_groups.pop(release_tag, None)
        this.module.depot_groups.pop(release_tag, None)
        this.module.simple_groups.pop(release_tag, None)
        this.descriptor.save_state()
    #
    gc.collect()
    #
    repo_core_settings = repo_core.get_settings()
    base_path = repo_core_settings.get("base_path", "/data/repo")
    #
    targets = [
        os.path.join(base_path, "public", "depot"),
        os.path.join(base_path, "public", "simple"),
        os.path.join(base_path, "depot"),
        os.path.join(base_path, "simple"),
    ]
    #
    log.info("Purging files")
    #
    for target in targets:
        target_path = os.path.join(target, release_tag)
        #
        if not os.path.exists(target_path):
            continue
        #
        shutil.rmtree(target_path)
