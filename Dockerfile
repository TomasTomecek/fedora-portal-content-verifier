FROM fedora:22
RUN dnf install -y docker git
ADD ./init.sh /
RUN chmod +x /init.sh
ENTRYPOINT /init.sh
