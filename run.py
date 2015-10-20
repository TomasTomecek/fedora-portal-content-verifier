#!/usr/bin/env python

import os
import logging
import subprocess

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


CI_ENV_VARS = [
    "TRAVIS",
    "CIRCLECI"
]


class Runner(object):
    def __init__(self):
        self.module_name = None

    def _run_in_ci(self):
        """
        run provided test
        """
        logging.info("running in CI: run localy test for module %r", self.module_name)
        subprocess.check_call("./%s/verify.sh" % self.module_name)

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
            return os.path.isdir(os.path.join(root_dir, d)) and d != ".git"
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

Overlord().run()
