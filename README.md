[![Circle CI](https://circleci.com/gh/TomasTomecek/fedora-portal-content-verifier.svg?style=svg)](https://circleci.com/gh/TomasTomecek/fedora-portal-content-verifier)

# fedora-portal-content-verifier

This is a very simple project for testing content in Fedora Developer Portal.


## How it works?

Tests for each module need to be in separate directory and root script needs to be named `verify.sh`:

```
docker-compose
└── verify.sh
```

Runner then spins new docker container for each module. The container has its [own clean docker daemon](https://github.com/jpetazzo/dind) running inside.
