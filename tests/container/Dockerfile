# Local mirror of the Linux CI job: Bash, Zsh, ShellCheck, Git, ripgrep, jq, ss.
FROM debian:bookworm-slim
ARG BASHUNIT_VERSION=0.50.1
ARG BASHUNIT_SHA256=18d83d590c5304f1853dd4fe4fec4ec6effbd9fe5a21831fe9f66f70afe17d93
RUN apt-get update \
 && apt-get install -y --no-install-recommends bash zsh git ripgrep shellcheck jq iproute2 \
      ca-certificates curl tar gzip python3 php-cli procps \
 && curl -fsSL "https://github.com/TypedDevs/bashunit/releases/download/$BASHUNIT_VERSION/bashunit" \
      -o /usr/local/bin/bashunit \
 && echo "$BASHUNIT_SHA256  /usr/local/bin/bashunit" | sha256sum -c - \
 && chmod +x /usr/local/bin/bashunit \
 && rm -rf /var/lib/apt/lists/*
