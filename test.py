from run import Runner


def test_run_in_ci():
    r = Runner("docker-compose")
    r._run_in_ci()
