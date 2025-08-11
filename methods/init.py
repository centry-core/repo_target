#!/usr/bin/python3
# coding=utf-8
# pylint: disable=C0411

""" Route """

# pylint: disable=E0401
from tools import web, auth, context, repo_core

from ..tasks import repo_tasks
from ..tasks import release_tasks


class Method:  # pylint: disable=E1101,R0903
    """ Method """

    # pylint: disable=W0201,R0912
    @web.init()
    def init(self):
        """ Init """
        auth.add_public_rule({"uri": f"{context.url_prefix}/target/public/.*"})
        #
        local_tasks = [
            ("list_repos", repo_tasks.list_repos_task),
            ("collect_release_files", release_tasks.collect_release_files_task),
            ("collect_release_requirements", release_tasks.collect_release_requirements_task),
        ]
        #
        for task_name, task_func in local_tasks:
            repo_core.register_task(task_name, task_func)
