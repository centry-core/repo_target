#!/usr/bin/python3
# coding=utf-8
# pylint: disable=C0411

""" Route """

import os
import threading

# pylint: disable=E0401
from tools import web, auth, context, repo_core, log

from ..tasks import repo_tasks
from ..tasks import registry_tasks
from ..tasks import release_tasks
from ..tasks import public_release_tasks


class Method:  # pylint: disable=E1101,R0903
    """ Method """

    # pylint: disable=W0201,R0912
    @web.init()
    def init(self):
        """ Init """
        #
        # Paths
        #
        repo_core_settings = repo_core.get_settings()
        base_path = repo_core_settings.get("base_path", "/data/repo")
        #
        cache_path = os.path.join(base_path, "cache")
        tmp_path = os.path.join(base_path, "tmp")
        #
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        #
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
            os.chmod(tmp_path, 0o1777)
        #
        # Auth
        #
        auth.add_public_rule({"uri": f"{context.url_prefix}/target/public/.*"})
        #
        # Lock
        #
        self.lock = threading.Lock()
        #
        # Registry
        #
        registry_just_initialized = False
        #
        if "repo_target_registry" not in self.descriptor.state:
            log.info("Registry not present: initializing")
            #
            self.descriptor.state["repo_target_registry"] = {
                "public_depot_groups": {},
                "public_simple_groups": {},
                "depot_groups": {},
                "simple_groups": {},
            }
            self.descriptor.save_state()
            #
            registry_just_initialized = True
        #
        # pylint: disable=C0301
        self.public_depot_groups = self.descriptor.state["repo_target_registry"]["public_depot_groups"]
        self.public_simple_groups = self.descriptor.state["repo_target_registry"]["public_simple_groups"]
        self.depot_groups = self.descriptor.state["repo_target_registry"]["depot_groups"]
        self.simple_groups = self.descriptor.state["repo_target_registry"]["simple_groups"]
        #
        if registry_just_initialized:
            registry_tasks.sync_registry_task()
        #
        # Tasks
        #
        # pylint: disable=C0301
        local_tasks = [
            ("list_repos", repo_tasks.list_repos_task),
            ("tag_release_from_main", repo_tasks.tag_release_from_main_task),
            ("sync_registry", registry_tasks.sync_registry_task),
            ("collect_release_files", release_tasks.collect_release_files_task),
            ("collect_release_requirements", release_tasks.collect_release_requirements_task),
            ("collect_public_release_files", public_release_tasks.collect_public_release_files_task),
            ("collect_public_release_requirements", public_release_tasks.collect_public_release_requirements_task),
        ]
        #
        for task_name, task_func in local_tasks:
            repo_core.register_task(task_name, task_func)
