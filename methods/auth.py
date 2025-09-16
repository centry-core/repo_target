#!/usr/bin/python3
# coding=utf-8
# pylint: disable=C0411

""" Method """

# pylint: disable=E0401
from tools import web, repo_core


class Method:  # pylint: disable=E1101,R0903
    """ Method """

    # pylint: disable=W0201,R0912
    @web.method()
    def is_internal_repo(self):
        """ Method """
        return self.descriptor.config.get("internal_repo", False)

    # pylint: disable=W0201,R0912
    @web.method()
    def auth_user_has_release(self, release):
        """ Method """
        if self.is_internal_repo():
            return True
        #
        return repo_core.user_has_release(release=release)
