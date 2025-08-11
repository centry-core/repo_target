#!/usr/bin/python3
# coding=utf-8

""" Task """

from tools import log, repo_core  # pylint: disable=E0401

from .common import GithubClient


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
