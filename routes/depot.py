#!/usr/bin/python3
# coding=utf-8

""" Route """

import flask  # pylint: disable=E0401

from tools import web, repo_core  # pylint: disable=E0401


class Route:  # pylint: disable=E1101,R0903
    """ Route """

    @web.route("/depot/")
    def depot_info(self):
        """ Route """
        if not repo_core.user_has_role(role="admin"):
            flask.abort(403)
        #
        result = {
            "groups": [],
        }
        #
        result["groups"].extend(sorted(list(self.depot_groups)))
        #
        return result

    @web.route("/depot/<group>/")
    def depot_group_info(self, group):
        """ Route """
        if not self.auth_user_has_release(release=group):
            flask.abort(403)
        #
        if group not in self.depot_groups:
            flask.abort(404)
        #
        result = {
            "plugins": [],
            "bundles": [],
        }
        #
        result["plugins"].extend(sorted(list(self.depot_groups[group]["plugins"])))
        result["bundles"].extend(sorted(list(self.depot_groups[group]["bundles"])))
        #
        return result

    @web.route("/depot/<group>/<entity>/<name>/")
    def depot_entity_info(self, group, entity, name):
        """ Route """
        if not self.auth_user_has_release(release=group):
            flask.abort(403)
        #
        if group not in self.depot_groups:
            flask.abort(404)
        #
        if entity not in self.depot_groups[group]:
            flask.abort(404)
        #
        if name not in self.depot_groups[group][entity]:
            flask.abort(404)
        #
        result = {
            "size": self.depot_groups[group][entity][name]["size"],
        }
        #
        return result

    @web.route("/depot/<group>/<entity>/<name>/<data>")
    def depot_entity_data(self, group, entity, name, data):
        """ Route """
        if not self.auth_user_has_release(release=group):
            flask.abort(403)
        #
        if group not in self.depot_groups:
            flask.abort(404)
        #
        if entity not in self.depot_groups[group]:
            flask.abort(404)
        #
        if name not in self.depot_groups[group][entity]:
            flask.abort(404)
        #
        if entity == "plugins":
            if data == "source":
                return flask.send_file(
                    self.depot_groups[group][entity][name]["file"],
                    as_attachment=True,
                    download_name=f"{name}.tar.gz",
                )
            #
            if data == "metadata":
                return self.depot_groups[group][entity][name]["metadata"]
            #
            if data == "requirements":
                response = flask.make_response(
                    self.depot_groups[group][entity][name]["requirements"].encode()
                )
                response.mimetype = "application/octet-stream"
                return response
        #
        if entity == "bundles":
            if data == "data":
                return flask.send_file(
                    self.depot_groups[group][entity][name]["file"],
                    as_attachment=True,
                    download_name=name,
                )
        #
        return flask.abort(404)
