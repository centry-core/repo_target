#!/usr/bin/python3
# coding=utf-8

""" Common """

import requests  # pylint: disable=E0401

from tools import log  # pylint: disable=E0401


class EliteAClient:  # pylint: disable=R0903,R0913
    """ Machinery """

    def __init__(self, elitea_url, elitea_token):
        self.elitea_url = elitea_url.rstrip("/")
        self.elitea_token = elitea_token
        #
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.elitea_token}",
            "User-Agent": "PythonMachineryEliteAClient",
        })

    def get_runtime_remote_heads(self):
        """ API """
        response = self.session.get(
            f"{self.elitea_url}/api/v1/admin/runtime_remote_heads/administration",
        )
        #
        return response.json()["rows"]

    def get_ui_head(self):
        """ API """
        response = self.session.get(
            f"{self.elitea_url}/alita_ui/static/ui/dist/head.txt",
        )
        #
        if response.status_code != 200:
            return None
        #
        return response.text


class GithubClient:  # pylint: disable=R0913
    """ Machinery """

    def __init__(self, github_token):
        self.github_token = github_token
        #
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.github_token}",
            "User-Agent": "PythonMachineryGithubClient",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def list_org_repos(self, org):
        """ API """
        result = []
        #
        target_url = f"https://api.github.com/orgs/{org}/repos"
        #
        while True:
            response = self.session.get(target_url)
            #
            result.extend(response.json())
            #
            if "next" not in response.links:
                break
            #
            target_url = response.links["next"]["url"]
        #
        return result

    def list_releases(self, owner, repo):
        """ API """
        result = []
        #
        target_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        #
        while True:
            response = self.session.get(target_url)
            #
            result.extend(response.json())
            #
            if "next" not in response.links:
                break
            #
            target_url = response.links["next"]["url"]
        #
        return result

    def get_repo(self, owner, repo):
        """ API """
        response = self.session.get(f"https://api.github.com/repos/{owner}/{repo}")
        #
        return response.json()

    def get_branch(self, owner, repo, branch):
        """ API """
        response = self.session.get(
            f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
        )
        #
        return response.json()

    def get_content(self, owner, repo, path, ref=None):
        """ API """
        params = {}
        #
        if ref is not None:
            params["ref"] = ref
        #
        response = self.session.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            params=params,
        )
        #
        return response.json()

    def get_tarball(self, owner, repo, ref, file=None):
        """ API """
        target_url = f"https://api.github.com/repos/{owner}/{repo}/tarball/{ref}"
        #
        if file is None:
            response = self.session.get(target_url)
            response.raise_for_status()
            #
            return response.content
        #
        with self.session.get(target_url, stream=True) as response:
            response.raise_for_status()
            #
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        #
        return file

    def get_zipball(self, owner, repo, ref, file=None):
        """ API """
        target_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{ref}"
        #
        if file is None:
            response = self.session.get(target_url)
            response.raise_for_status()
            #
            return response.content
        #
        with self.session.get(target_url, stream=True) as response:
            response.raise_for_status()
            #
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        #
        return file

    def get_auth_user(self):
        """ API """
        response = self.session.get("https://api.github.com/user")
        #
        return response.json()

    def create_tag(  # pylint: disable=R0917
            self,
            owner, repo,
            tag_name, tag_message,
            target_object, target_type="commit",
        ):
        """ API """
        response = self.session.post(
            f"https://api.github.com/repos/{owner}/{repo}/git/tags",
            json={
                "tag": tag_name,
                "message": tag_message,
                "object": target_object,
                "type": target_type,
            },
        )
        #
        return response.json()

    def create_ref(
            self,
            owner, repo,
            ref_name, ref_sha,
        ):
        """ API """
        response = self.session.post(
            f"https://api.github.com/repos/{owner}/{repo}/git/refs",
            json={
                "ref": ref_name,
                "sha": ref_sha,
            },
        )
        #
        return response.json()

    def update_ref(  # pylint: disable=R0917
            self,
            owner, repo,
            ref_name, ref_sha,
            force=False,
        ):
        """ API """
        response = self.session.patch(
            f"https://api.github.com/repos/{owner}/{repo}/git/refs/{ref_name}",
            json={
                "sha": ref_sha,
                "force": force,
            },
        )
        #
        return response.json()

    def create_or_update_tag_and_ref(  # pylint: disable=R0917
            self,
            owner, repo,
            tag_name, tag_message,
            target_object, target_type="commit",
        ):
        """ API """
        tag = self.create_tag(
            owner, repo,
            tag_name, tag_message,
            target_object, target_type,
        )
        #
        if "tag" not in tag or "sha" not in tag:
            raise RuntimeError(f"Failed to create tag: {tag}")
        #
        ref = self.create_ref(
            owner, repo,
            f'refs/tags/{tag["tag"]}', tag["sha"],
        )
        #
        if ref.get("message", None) == "Reference already exists":
            ref = self.update_ref(
                owner, repo,
                f'tags/{tag["tag"]}', tag["sha"],
                force=True,
            )
        #
        ref_message = ref.get("message", None)
        #
        if ref_message is not None:
            raise RuntimeError(ref_message)
        #
        return ref
