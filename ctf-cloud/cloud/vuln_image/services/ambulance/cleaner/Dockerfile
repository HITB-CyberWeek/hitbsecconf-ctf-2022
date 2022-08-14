FROM ubuntu:20.04

RUN useradd --no-create-home --shell /bin/false --uid 1000 --user-group cleaner

COPY cleaner.sh /var/cleaner.sh

RUN chmod +x /var/cleaner.sh

USER cleaner

ENTRYPOINT ["/var/cleaner.sh"]
