#!/usr/bin/python3
# coding=utf-8

""" Route """

import json

import flask  # pylint: disable=E0401

from tools import web, repo_core  # pylint: disable=E0401


class Route:  # pylint: disable=E1101,R0903
    """ Route """

    @web.route("/simple/")
    def simple_info(self):
        """ Route """
        if not repo_core.user_has_role(role="admin"):
            flask.abort(403)
        #
        result = {
            "groups": [],
        }
        #
        result["groups"].extend(sorted(list(self.simple_groups)))
        #
        return result

    @web.route("/simple/<group>/")
    def project_list(self, group):
        """ Route """
        if not repo_core.user_has_release(release=group):
            flask.abort(403)
        #
        if group not in self.simple_groups:
            flask.abort(404)
        #
        result = {
            "meta": {
                "api-version": "1.3"
            },
            "projects": [],
        }
        #
        for project_name in list(self.simple_groups[group]):
            result["projects"].append({
                "name": project_name,
            })
        #
        response = flask.make_response(json.dumps(result))
        response.mimetype = "application/vnd.pypi.simple.v1+json"
        #
        return response

    @web.route("/simple/<group>/<project>/")
    def project_detail(self, group, project):
        """ Route """
        if not repo_core.user_has_release(release=group):
            flask.abort(403)
        #
        if group not in self.simple_groups:
            flask.abort(404)
        #
        if project not in self.simple_groups[group]:
            flask.abort(404)
        #
        result = {
            "meta": {
                "api-version": "1.3"
            },
            "name": project,
            "files": [],
            "versions": set(),
        }
        #
        for file_name in list(self.simple_groups[group][project]):
            wheel_item = self.simple_groups[group][project][file_name]
            #
            result_item = {
                "filename": file_name,
                "url": flask.url_for(
                    "pypi_simple.wheel",
                    project=project,
                    wheel=file_name,
                    _external=True,
                ),
                "hashes": wheel_item["hashes"],
                "core-metadata": wheel_item["metadata_hashes"],
                "size": wheel_item["size"],
            }
            #
            if wheel_item["requires_python"] is not None:
                result_item["requires-python"] = wheel_item["requires_python"]
            #
            result["files"].append(result_item)
            #
            result["versions"].add(wheel_item["version"])
        #
        result["versions"] = list(result["versions"])
        #
        response = flask.make_response(json.dumps(result))
        response.mimetype = "application/vnd.pypi.simple.v1+json"
        #
        return response

    @web.route("/simple/<group>/<project>/<wheel>")
    def wheel(self, group, project, wheel):
        """ Route """
        if not repo_core.user_has_release(release=group):
            flask.abort(403)
        #
        if group not in self.simple_groups:
            flask.abort(404)
        #
        if project not in self.simple_groups[group]:
            flask.abort(404)
        #
        if wheel not in self.simple_groups[group][project]:
            flask.abort(404)
        #
        return flask.send_file(
            self.simple_groups[group][project][wheel]["file"],
            as_attachment=True,
            download_name=wheel,
        )

    @web.route("/simple/<group>/<project>/<wheel>.metadata")
    def wheel_metadata(self, group, project, wheel):
        """ Route """
        if not repo_core.user_has_release(release=group):
            flask.abort(403)
        #
        if group not in self.simple_groups:
            flask.abort(404)
        #
        if project not in self.simple_groups[group]:
            flask.abort(404)
        #
        if wheel not in self.simple_groups[group][project]:
            flask.abort(404)
        #
        response = flask.make_response(self.simple_groups[group][project][wheel]["metadata"])
        response.mimetype = "application/octet-stream"
        #
        return response
