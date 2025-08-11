#!/usr/bin/python3
# coding=utf-8

""" Route """

import flask  # pylint: disable=E0401

from tools import web  # pylint: disable=E0401


class Route:  # pylint: disable=E1101,R0903
    """ Route """

    @web.route("/public/depot/")
    def public_depot_info(self):
        """ Route """
        result = {
            "groups": [],
        }
        #
        result["groups"].extend(sorted(list(self.public_depot_groups)))
        #
        return result

    @web.route("/public/depot/<group>/")
    def public_depot_group_info(self, group):
        """ Route """
        if group not in self.public_depot_groups:
            flask.abort(404)
        #
        result = {
            "plugins": [],
            "bundles": [],
        }
        #
        result["plugins"].extend(sorted(list(self.public_depot_groups[group]["plugins"])))
        result["bundles"].extend(sorted(list(self.public_depot_groups[group]["bundles"])))
        #
        return result

    @web.route("/public/depot/<group>/<entity>/<name>/")
    def public_depot_entity_info(self, group, entity, name):
        """ Route """
        if group not in self.public_depot_groups:
            flask.abort(404)
        #
        if entity not in self.public_depot_groups[group]:
            flask.abort(404)
        #
        if name not in self.public_depot_groups[group][entity]:
            flask.abort(404)
        #
        result = {
            "size": self.public_depot_groups[group][entity][name]["size"],
        }
        #
        return result

    @web.route("/public/depot/<group>/<entity>/<name>/<data>")
    def public_depot_entity_data(self, group, entity, name, data):
        """ Route """
        if group not in self.public_depot_groups:
            flask.abort(404)
        #
        if entity not in self.public_depot_groups[group]:
            flask.abort(404)
        #
        if name not in self.public_depot_groups[group][entity]:
            flask.abort(404)
        #
        if entity == "plugins":
            if data == "source":
                return flask.send_file(
                    self.public_depot_groups[group][entity][name]["file"],
                    as_attachment=True,
                    download_name=f"{name}.tar.gz",
                )
            #
            if data == "metadata":
                return self.public_depot_groups[group][entity][name]["metadata"]
            #
            if data == "requirements":
                response = flask.make_response(
                    self.public_depot_groups[group][entity][name]["requirements"]
                )
                response.mimetype = "application/octet-stream"
                return response
        #
        if entity == "bundles":
            if data == "data":
                return flask.send_file(
                    self.public_depot_groups[group][entity][name]["file"],
                    as_attachment=True,
                    download_name=name,
                )
        #
        return flask.abort(404)
