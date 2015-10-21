#!/usr/bin/env python

"""
TODO:
 * use docker-py & get rid of subprocess
"""

import os
import pipes
import argparse
import logging
import subprocess
import tempfile
import shutil

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


CI_ENV_VARS = [
    "TRAVIS",
    "CIRCLECI"
]

IGNORE_MODULES = [".git", "venv"]

DOWNLOAD_AND_RUN_TEST_SH = """\
set -ex ; \
cd / ; \
curl -sSL -O https://get.docker.com/builds/Linux/x86_64/docker-1.6.2 ; \
chmod +x docker-1.6.2 ; \
sudo mv docker-1.6.2 /usr/local/bin/docker ; \
curl -s -o /run.py https://raw.githubusercontent.com/TomasTomecek/fedora-portal-content-verifier/master/run.py ; \
chmod +x /run.py ; \
exec /run.py --local {module_name:s} \
"""


class Runner(object):
    def __init__(self, module_name=None):
        self.module_name = module_name

    def _run_in_ci(self):
        """
        in CI, we have clean docker environment (dind most likely)

        let's spawn new container (fedora), bindmount docker socket there and
        run all tests in such env
        """
        logging.info("running in CI: run test for module %r", self.module_name)
        subprocess.check_call([
            "docker", "run",
            "-v", "/run/docker.sock:/run/docker.sock",
            "--rm",
            "fedora", "bash", "-c", DOWNLOAD_AND_RUN_TEST_SH.format(module_name=self.module_name)
        ])

    def run_locally(self):
        """
        run provided test in current environment
        """
        tmpdir = tempfile.mkdtemp()
        try:
            subprocess.check_call(["dnf", "install", "-y", "git"])
            subprocess.check_call(
                [
                    "git",
                    "clone",
                    "https://github.com/TomasTomecek/fedora-portal-content-verifier",
                    "repo",
                ],
                cwd=tmpdir
            )
            subprocess.check_call("./%s/verify.sh" % self.module_name, cwd=os.path.join(tmpdir, "repo"))
        finally:
            shutil.rmtree(tmpdir)

    def _run_nested(self):
        """
        spawn new docker and run a provided test
        """
        subprocess.check_call([
            "docker", "run",
            "--privileged",
            "-e DOCKER_DAEMON_ARGS=\"-D -l debug\"",
            "--rm", "-it",
            "d", self.module_name
        ])

    def run(self, module_name):
        """
        run test for provided module
        """
        self.module_name = module_name
        if set(os.environ.keys()).intersection(CI_ENV_VARS):
            self._run_in_ci()
        else:
            self._run_nested()


class Overlord(object):
    """
    find all modules and run their tests
    """

    def __init__(self):
        self.runner = Runner()

    def find_modules(self):
        def module_filter(d):
            return os.path.isdir(os.path.join(root_dir, d)) and d not in IGNORE_MODULES
        root_dir = os.path.abspath(os.path.dirname(__file__))
        logging.debug("root_dir = %r", root_dir)
        all_files = os.listdir(root_dir)
        logging.debug("all_files = %s", all_files)
        return [x for x in all_files if module_filter(x)]

    def run(self):
        modules = self.find_modules()
        logging.debug("modules = %s", modules)
        for m in modules:
            self.runner.run(m)


def main():
    parser = argparse.ArgumentParser(
        description="run tests in fresh clean container",
    )
    parser.add_argument("--init", action="store_true", help="initiate tests for all modules")
    parser.add_argument("--local", action="store", help="run test for provided module in current environment")
    # parser.add_argument("--inject", action="store_true", help="spawn new container, mount docker socket inside and run provided test there")
    args = parser.parse_args()

    if args.local:
        r = Runner(args.local)
        r.run_locally()
    else:  # --init is default
        Overlord().run()


if __name__ == "__main__":
    main()

