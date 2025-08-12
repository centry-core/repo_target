#!/usr/bin/python3
# coding=utf-8

""" Task """

import os
import gc
import tarfile
import tempfile

from tools import log, repo_core, this  # pylint: disable=E0401
from pylon.core.tools import process  # pylint: disable=E0401

from .common import GithubClient


def collect_public_release_files_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    release_tag = kwargs["param"]
    #
    if not release_tag:
        log.error("Release not specified")
        return
    #
    config = repo_core.get_settings()
    github_client = GithubClient(config["github_token"])
    #
    base_path = config.get("base_path", "/data/repo")
    depot_path = os.path.join(base_path, "public", "depot")
    #
    plugins_path = os.path.join(depot_path, release_tag, "plugins")
    bundles_path = os.path.join(depot_path, release_tag, "bundles")
    #
    if not os.path.exists(plugins_path):
        os.makedirs(plugins_path)
    #
    if not os.path.exists(bundles_path):
        os.makedirs(bundles_path)
    #
    for org in config["target_orgs"]:  # pylint: disable=R1702
        for repo_name in config["known_repos"]["public_target"][org]:
            log.info("Collecting public depot data: %s - %s", org, repo_name)
            #
            metadata_content = github_client.get_content(
                org, repo_name, "metadata.json",
                ref=release_tag,
            )
            #
            if "content" in metadata_content:
                log.info("- Getting plugin data")
                # NOTE: Can use name from metadata too?
                plugin_path = os.path.join(plugins_path, f"{repo_name}.tar.gz")
                #
                with open(plugin_path, "wb") as file:
                    github_client.get_tarball(org, repo_name, release_tag, file=file)
            else:
                releases = github_client.list_releases(org, repo_name)
                #
                for release_info in releases:
                    if release_info["name"] == release_tag:
                        log.info("- Getting bundle data")
                        #
                        asset = release_info["assets"][0]
                        file_ext = os.path.splitext(asset["name"])[1]
                        bundle_path = os.path.join(bundles_path, f"{repo_name}{file_ext}")
                        #
                        response = github_client.session.get(asset["url"], stream=True)
                        if response.ok:
                            with open(bundle_path, "wb") as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)
                        response.close()
            #
            gc.collect()
    #
    log.info("Updating registry")
    #
    this.module.public_depot_groups[release_tag] = {
        "plugins": this.module.collect_depot_group_plugins(plugins_path),
        "bundles": this.module.collect_depot_group_bundles(bundles_path),
    }
    #
    gc.collect()


def collect_public_release_requirements_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    release_tag = kwargs["param"]
    #
    if not release_tag:
        log.error("Release not specified")
        return
    #
    config = repo_core.get_settings()
    #
    base_path = config.get("base_path", "/data/repo")
    depot_path = os.path.join(base_path, "public", "depot")
    simple_path = os.path.join(base_path, "public", "simple")
    cache_path = os.path.join(base_path, "cache")
    tmp_path = os.path.join(base_path, "tmp")
    #
    plugins_path = os.path.join(depot_path, release_tag, "plugins")
    requirements_path = os.path.join(simple_path, release_tag)
    #
    if not os.path.exists(plugins_path):
        return
    #
    if not os.path.exists(requirements_path):
        os.makedirs(requirements_path)
    #
    for file_name in os.listdir(plugins_path):
        if not file_name.endswith(".tar.gz"):
            continue
        #
        file_path = os.path.join(plugins_path, file_name)
        #
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
                if member_name == "requirements.txt":
                    try:
                        plugin_requirements = file.extractfile(member).read()
                    except:  # pylint: disable=W0702
                        pass
                #
                if plugin_requirements is not None:
                    break
        #
        gc.collect()
        #
        if plugin_requirements is None:
            continue
        #
        log.info("Getting requirements: %s", file_name)
        #
        requirements_txt_fd, requirements_txt = tempfile.mkstemp(".txt")
        os.close(requirements_txt_fd)
        #
        try:
            with open(requirements_txt, "wb") as file:
                file.write(plugin_requirements)
            #
            env = os.environ.copy()
            env["TMPDIR"] = tmp_path
            #
            process.run_command(
                [
                    "pip3", "wheel",
                    "--isolated",
                    "--no-cache-dir",
                    "--cache-dir", cache_path,
                    # "--extra-index-url", "https://download.pytorch.org/whl/cpu",
                    "--wheel-dir", requirements_path,
                    "--requirement", requirements_txt,
                ],
                env=env,
            )
        finally:
            os.remove(requirements_txt)
            gc.collect()
    #
    log.info("Updating registry")
    #
    this.module.public_simple_groups[release_tag] = this.module.collect_simple_group_wheels(
        requirements_path
    )
    #
    gc.collect()
