#!/usr/bin/python3
# coding=utf-8

""" Task """

import os
import base64
import shutil

from tools import log, repo_core  # pylint: disable=E0401
from pylon.core.tools import process  # pylint: disable=E0401,E0611

from .common import GithubClient
from .common import EliteAClient


def diff_stage_migrations_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    whitelist = []
    #
    config = repo_core.get_settings()
    #
    base_path = config.get("base_path", "/data/repo")
    diffs_path = os.path.join(base_path, "diffs")
    #
    prev_path = os.path.join(diffs_path, "prev")
    next_path = os.path.join(diffs_path, "next")
    #
    if os.path.exists(prev_path):
        shutil.rmtree(prev_path)
    #
    if os.path.exists(next_path):
        shutil.rmtree(next_path)
    #
    if not os.path.exists(prev_path):
        os.makedirs(prev_path)
    #
    if not os.path.exists(next_path):
        os.makedirs(next_path)
    #
    elitea_client = EliteAClient(config["elitea_url"], config["elitea_token"])
    github_client = GithubClient(config["github_token"])
    #
    plugin_map = {}
    #
    for org in config["target_orgs"]:
        for target_name in config["known_repos"]["target"].get(org, []):
            if target_name in plugin_map:
                raise RuntimeError(f"Duplicate name: {target_name}")
            #
            if whitelist and target_name not in whitelist:
                continue
            #
            plugin_map[target_name] = {
                "org": org,
                "repo": target_name,
            }
    #
    remote_heads = elitea_client.get_runtime_remote_heads()
    #
    applied_plugins = set()
    #
    for head_info in sorted(remote_heads, key=lambda item: item["plugin_name"]):
        plugin_name = head_info["plugin_name"]
        plugin_head = head_info["git_head"]
        #
        if plugin_head is None:
            log.error("No head info: %s", plugin_name)
            continue
        #
        if plugin_name not in plugin_map:
            log.warning("Unknown/not whitelisted plugin: %s", plugin_name)
            continue
        #
        plugin_info = plugin_map[plugin_name]
        #
        try:
            log.info("Getting prev: %s - %s", plugin_info["org"], plugin_info["repo"])
            #
            prev_content = github_client.get_content(
                plugin_info["org"], plugin_info["repo"], "db_migrations.txt",
                ref=plugin_head,
            )
            #
            if "content" in prev_content:
                with open(os.path.join(prev_path, f"{plugin_name}.txt"), "wb") as file:
                    file.write(base64.b64decode(prev_content["content"]))
            #
            log.info("Getting next: %s - %s", plugin_info["org"], plugin_info["repo"])
            #
            next_content = github_client.get_content(
                plugin_info["org"], plugin_info["repo"], "db_migrations.txt",
                ref="staging",
            )
            #
            if "content" in next_content:
                with open(os.path.join(next_path, f"{plugin_name}.txt"), "wb") as file:
                    file.write(base64.b64decode(next_content["content"]))
        except:  # pylint: disable=W0702
            log.exception("Failed to get: %s - %s", plugin_info["org"], plugin_info["repo"])
        #
        applied_plugins.add(plugin_name)
    #
    for plugin_name in sorted(plugin_map):
        if plugin_name not in applied_plugins:
            plugin_info = plugin_map[plugin_name]
            #
            try:
                log.info("Getting next: %s - %s", plugin_info["org"], plugin_info["repo"])
                #
                next_content = github_client.get_content(
                    plugin_info["org"], plugin_info["repo"], "db_migrations.txt",
                    ref="staging",
                )
                #
                if "content" in next_content:
                    with open(os.path.join(next_path, f"{plugin_name}.txt"), "wb") as file:
                        file.write(base64.b64decode(next_content["content"]))
            except:  # pylint: disable=W0702
                log.exception("Failed to get: %s - %s", plugin_info["org"], plugin_info["repo"])
    #
    log.info("- - - - - - - - -")
    #
    try:
        process.run_command(
            [
                "diff", "-Naru", "prev", "next",
            ],
            cwd=diffs_path,
        )
    except:  # pylint: disable=W0702
        pass  # we expect to have return code 1 when there are changes
    #
    shutil.rmtree(diffs_path)


def diff_release_migrations_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    target_param = kwargs["param"].strip()
    #
    if not target_param:
        log.error("Please specify prev-next release names")
        return
    #
    whitelist = []
    #
    if ":" in target_param:
        target_param, whitelist_data = target_param.split(":", 1)
        whitelist = whitelist_data.split(",")
    #
    prev_release, next_release = target_param.split(",", 1)
    #
    config = repo_core.get_settings()
    #
    base_path = config.get("base_path", "/data/repo")
    diffs_path = os.path.join(base_path, "diffs")
    #
    prev_path = os.path.join(diffs_path, "prev")
    next_path = os.path.join(diffs_path, "next")
    #
    if os.path.exists(prev_path):
        shutil.rmtree(prev_path)
    #
    if os.path.exists(next_path):
        shutil.rmtree(next_path)
    #
    if not os.path.exists(prev_path):
        os.makedirs(prev_path)
    #
    if not os.path.exists(next_path):
        os.makedirs(next_path)
    #
    github_client = GithubClient(config["github_token"])
    #
    for org in config["target_orgs"]:
        for target_name in config["known_repos"]["target"].get(org, []):
            if whitelist and target_name not in whitelist:
                continue
            #
            try:
                log.info("Getting prev: %s - %s", org, target_name)
                #
                prev_content = github_client.get_content(
                    org, target_name, "db_migrations.txt",
                    ref=prev_release,
                )
                #
                with open(os.path.join(prev_path, f"{target_name}.txt"), "wb") as file:
                    if "content" in prev_content:
                        file.write(base64.b64decode(prev_content["content"]))
                #
                log.info("Getting next: %s - %s", org, target_name)
                #
                next_content = github_client.get_content(
                    org, target_name, "db_migrations.txt",
                    ref=next_release,
                )
                #
                with open(os.path.join(next_path, f"{target_name}.txt"), "wb") as file:
                    if "content" in next_content:
                        file.write(base64.b64decode(next_content["content"]))
            except:  # pylint: disable=W0702
                log.exception("Failed to get: %s - %s", org, target_name)
    #
    log.info("- - - - - - - - -")
    #
    try:
        process.run_command(
            [
                "diff", "-Naru", "prev", "next",
            ],
            cwd=diffs_path,
        )
    except:  # pylint: disable=W0702
        pass  # we expect to have return code 1 when there are changes
    #
    shutil.rmtree(diffs_path)
