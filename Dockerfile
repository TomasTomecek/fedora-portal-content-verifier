FROM fedora:22
RUN dnf install -y git python-docker-py
RUN git clone https://github.com/TomasTomecek/fedora-portal-content-verifier /repo || : || :
WORKDIR /repo
ENTRYPOINT ["/repo/run.py"]
