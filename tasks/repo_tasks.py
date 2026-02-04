#!/usr/bin/python3
# coding=utf-8

""" Task """

from tools import log, repo_core  # pylint: disable=E0401

from .common import GithubClient
from .common import EliteAClient


def list_repos_task(*_args, **_kwargs):
    """ Task """
    config = repo_core.get_settings()
    #
    github_client = GithubClient(config["github_token"])
    #
    for org in config["target_orgs"]:
        log.info("Listing repos: %s", org)
        #
        repos = github_client.list_org_repos(org)
        #
        unknown_repos = []
        #
        for repo in repos:
            repo_name = repo["name"]
            #
            if repo_name not in config["known_repos"]["target"][org] and \
                    repo_name not in config["known_repos"]["ignore"][org]:
                unknown_repos.append(repo_name)
        #
        unknown_repos.sort()
        #
        if unknown_repos:
            log.info("Unknown (new) repos:")
            for repo_name in unknown_repos:
                log.info("- %s", repo_name)


def tag_release_from_main_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    release_tag = kwargs["param"]
    #
    if not release_tag:
        log.error("Release not specified")
        return
    #
    log.info("Target: %s", release_tag)
    #
    whitelist = []
    #
    if ":" in release_tag:
        release_tag, whitelist_data = release_tag.split(":", 1)
        whitelist = whitelist_data.split(",")
    #
    release_tag_message = release_tag
    #
    config = repo_core.get_settings()
    github_client = GithubClient(config["github_token"])
    #
    for org in config["target_orgs"]:  # pylint: disable=R1702
        for repo_name in config["known_repos"]["target"][org]:
            if whitelist and repo_name not in whitelist:
                continue
            #
            log.info("Tagging from main: %s - %s", org, repo_name)
            #
            try:
                repo = github_client.get_repo(org, repo_name)
                branch = github_client.get_branch(
                    org, repo_name, repo["default_branch"]
                )
                #
                github_client.create_or_update_tag_and_ref(
                    org, repo_name,
                    release_tag, release_tag_message,
                    branch["commit"]["sha"],
                )
            except:  # pylint: disable=W0702
                log.exception("Failed to apply tag: %s - %s", org, repo_name)


def tag_release_from_stage_task(*_args, **kwargs):  # pylint: disable=R0912,R0914,R0915
    """ Task """
    release_tag = kwargs["param"]
    #
    if not release_tag:
        log.error("Release not specified")
        return
    #
    log.info("Target: %s", release_tag)
    #
    whitelist = []
    #
    if ":" in release_tag:
        release_tag, whitelist_data = release_tag.split(":", 1)
        whitelist = whitelist_data.split(",")
    #
    release_tag_message = release_tag
    #
    config = repo_core.get_settings()
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
    ui_head = elitea_client.get_ui_head()
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
            log.info("Tagging from stage: %s - %s", plugin_info["org"], plugin_info["repo"])
            #
            github_client.create_or_update_tag_and_ref(
                plugin_info["org"], plugin_info["repo"],
                release_tag, release_tag_message,
                plugin_head,
            )
        except:  # pylint: disable=W0702
            log.exception("Failed to apply tag: %s - %s", plugin_info["org"], plugin_info["repo"])
        #
        applied_plugins.add(plugin_name)
    #
    for plugin_name in sorted(plugin_map):
        if plugin_name not in applied_plugins:
            plugin_info = plugin_map[plugin_name]
            #
            if plugin_name == "AlitaUI" and ui_head is not None:
                try:
                    log.info("Tagging from stage: %s - %s", plugin_info["org"], plugin_info["repo"])
                    #
                    github_client.create_or_update_tag_and_ref(
                        plugin_info["org"], plugin_info["repo"],
                        release_tag, release_tag_message,
                        ui_head,
                    )
                except:  # pylint: disable=W0702
                    log.exception(
                        "Failed to apply tag: %s - %s", plugin_info["org"], plugin_info["repo"]
                    )
            else:
                log.info("Tagging from main: %s - %s", plugin_info["org"], plugin_info["repo"])
                #
                try:
                    repo = github_client.get_repo(plugin_info["org"], plugin_info["repo"])
                    branch = github_client.get_branch(
                        plugin_info["org"], plugin_info["repo"], repo["default_branch"]
                    )
                    #
                    github_client.create_or_update_tag_and_ref(
                        plugin_info["org"], plugin_info["repo"],
                        release_tag, release_tag_message,
                        branch["commit"]["sha"],
                    )
                except:  # pylint: disable=W0702
                    log.exception(
                        "Failed to apply tag: %s - %s", plugin_info["org"], plugin_info["repo"]
                    )


#
# ---
#


def delete_staging_branch_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    target_param = kwargs["param"].strip()
    #
    whitelist = []
    #
    if target_param:
        whitelist = target_param.split(",")
    #
    config = repo_core.get_settings()
    github_client = GithubClient(config["github_token"])
    #
    staging_name = "staging"
    #
    for org in config["target_orgs"]:  # pylint: disable=R1702
        for repo_name in config["known_repos"]["target"][org]:
            if whitelist and repo_name not in whitelist:
                continue
            #
            log.info("Deleting staging: %s - %s", org, repo_name)
            #
            try:
                staging_ref = github_client.get_ref(org, repo_name, f"heads/{staging_name}")
                #
                if "ref" in staging_ref:
                    github_client.delete_ref(
                        org, repo_name,
                        f"heads/{staging_name}",
                    )
                    #
                    log.info("Deleted existing staging ref")
                else:
                    log.info("Staging ref not found")
            except:  # pylint: disable=W0702
                log.exception("Failed to delete stage: %s - %s", org, repo_name)


def make_release_branch_from_main_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    target_param = kwargs["param"].strip()
    #
    if not target_param:
        log.error("Please specify release name")
        return
    #
    whitelist = []
    #
    if ":" in target_param:
        target_param, whitelist_data = target_param.split(":", 1)
        whitelist = whitelist_data.split(",")
    #
    config = repo_core.get_settings()
    github_client = GithubClient(config["github_token"])
    #
    source_name = "main"
    release_name = target_param
    release_branch_name = f"release/{release_name}"
    #
    for org in config["target_orgs"]:  # pylint: disable=R1702
        for repo_name in config["known_repos"]["target"][org]:
            if whitelist and repo_name not in whitelist:
                continue
            #
            log.info("Making %s from %s: %s - %s", release_name, source_name, org, repo_name)
            #
            try:
                source_branch = github_client.get_branch(org, repo_name, source_name)
                release_ref = github_client.get_ref(org, repo_name, f"heads/{release_branch_name}")
                #
                if "ref" in release_ref:
                    log.warning("Release branch already exists")
                else:
                    new_ref = github_client.create_ref(
                        org, repo_name,
                        f"refs/heads/{release_branch_name}",
                        source_branch["commit"]["sha"],
                    )
                    #
                    log.info("Created ref: %s", new_ref)
            except:  # pylint: disable=W0702
                log.exception("Failed to make: %s - %s", org, repo_name)


def tag_release_task(*_args, **kwargs):  # pylint: disable=R0912,R0914
    """ Task """
    target_param = kwargs["param"].strip()
    #
    if not target_param:
        log.error("Please specify release name")
        return
    #
    whitelist = []
    #
    if ":" in target_param:
        target_param, whitelist_data = target_param.split(":", 1)
        whitelist = whitelist_data.split(",")
    #
    config = repo_core.get_settings()
    github_client = GithubClient(config["github_token"])
    #
    release_name = target_param
    release_tag_message = release_name
    release_branch_name = f"release/{release_name}"
    #
    for org in config["target_orgs"]:  # pylint: disable=R1702
        for repo_name in config["known_repos"]["target"][org]:
            if whitelist and repo_name not in whitelist:
                continue
            #
            log.info("Tagging %s: %s - %s", release_name, org, repo_name)
            #
            try:
                release_ref = github_client.get_ref(org, repo_name, f"heads/{release_branch_name}")
                #
                if "ref" not in release_ref:
                    log.warning("Release branch does not exist")
                    continue
                #
                release_branch = github_client.get_branch(org, repo_name, release_branch_name)
                #
                github_client.create_or_update_tag_and_ref(
                    org, repo_name,
                    release_name, release_tag_message,
                    release_branch["commit"]["sha"],
                )
            except:  # pylint: disable=W0702
                log.exception("Failed to tag: %s - %s", org, repo_name)
