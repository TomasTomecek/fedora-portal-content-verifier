#!/usr/bin/env python

"""
TODO:
"""

import os
import re
import argparse
import logging
import subprocess

import docker
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


CI_ENV_VARS = [
    "TRAVIS",
    "CIRCLECI"
]

REPO_PATH = "/repo"
CONTENT_PATH = "content/"
SCRIPT_NAME = "verify.sh"

IMAGE = "tomastomecek/fedora-portal-content-verifier"

DOCKER_BINS = "https://get.docker.com/builds/Linux/x86_64/docker-{version:s}"
DOCKER_BIN_PATH = "/usr/local/bin/docker"


class Runner(object):
    def __init__(self, module_name=None, nested=False, spawn_dind=False):
        self.module_name = module_name
        self.nested = nested
        if spawn_dind:
            self.spawn_dind = True
            self.module_name = spawn_dind

    def _run_in_container(self):
        """
        in CI, we have clean docker environment (dind most likely)

        let's spawn new container (fedora), bindmount docker socket there and
        run all tests in such env
        """
        logging.info("running test in container: run test for module %r", self.module_name)
        self._install_docker()
        if self.spawn_dind:
            logging.info("running wrapdocker")
            wrapdocker_path = os.path.join(REPO_PATH, "wrapdocker")
            subprocess.check_call([wrapdocker_path])

        subprocess.check_call([
            "docker", "run",
            "-v", "/run/docker.sock:/run/docker.sock",
            "--rm",
            IMAGE, "--local"
        ])

    def _install_docker(self):
        logging.info("install docker in current environment")
        d = docker.AutoVersionClient()
        try:
            version_chain = d.version()["Version"]
        except Exception as ex:
            logging.debug("%r", ex)
            with open("/etc/issue") as fd:
                is_fedora = "Fedora" in fd.read()
                version = "1.8.2"
        else:
            version = re.findall(r"(\d+\.\d+\.\d+)", version_chain)[0]
            is_fedora = bool(re.findall(r"-fc\d{2}$", version_chain))

        if is_fedora:
            logging.info("docker server is fedora")
            subprocess.check_call(["dnf", "install", "-y", "docker"])
        else:
            logging.info("get docker %r from docker", version)
            url = DOCKER_BINS.format(version=version)
            r = requests.get(url, stream=True)
            with open(DOCKER_BIN_PATH, "wb") as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        fd.write(chunk)
            os.chmod(DOCKER_BIN_PATH, "0755")

    def run_locally(self):
        """
        run provided test in current environment
        """
        logging.info("running locally")

        self._install_docker()

        logging.info("execute verify script")
        verify_script_path = os.path.join(REPO_PATH, CONTENT_PATH, self.module_name, SCRIPT_NAME)
        subprocess.check_call(verify_script_path)

    def _run_nested(self):
        """
        1. spawn new privileged container with dind inside
        2. use CI method
        """
        subprocess.check_call([
            "docker", "run",
            "--privileged",
            "-e", "DOCKER_DAEMON_ARGS=\"-D -l debug\"",
            "--rm", "-it",
            IMAGE, "--spawn-dind", self.module_name
        ])

    def run(self, module_name):
        """
        run test for provided module
        """
        self.module_name = module_name
        if self.nested:
            self._run_nested()
        # elif set(os.environ.keys()).intersection(CI_ENV_VARS):
        else:
            self._run_in_container()


class Overlord(object):
    """
    find all modules and run their tests
    """

    def __init__(self, nested=False, spawn_dind=False):
        self.runner = Runner(nested=nested, spawn_dind=spawn_dind)

    def find_modules(self):
        root_dir = os.path.abspath(os.path.dirname(__file__))
        logging.debug("root_dir = %r", root_dir)
        content_dir = os.path.join(root_dir, CONTENT_PATH)
        logging.debug("content_dir = %s", content_dir)
        modules = os.listdir(content_dir)
        logging.debug("modules = %s", modules)
        return modules

    def run(self):
        modules = self.find_modules()
        for m in modules:
            self.runner.run(m)


def main():
    parser = argparse.ArgumentParser(
        description="run tests in fresh clean container",
    )
    parser.add_argument("--init", action="store_true", help="initiate tests for all modules")
    parser.add_argument("--nested", action="store_true", help="run all modules in a container which spawns dind")

    parser.add_argument("--local", action="store", help="run test for provided module in current environment")
    parser.add_argument("--spawn-dind", action="store", help="spawn dind and run test in a new container")
    args = parser.parse_args()

    if args.local:
        r = Runner(args.local)
        r.run_locally()
    else:  # --init is default
        Overlord(nested=args.nested, spawn_dind=args.spawn_dind).run()


if __name__ == "__main__":
    main()

