# Local mirror of the Linux CI job: Bash, Zsh, ShellCheck, Git, ripgrep, jq, ss.
FROM debian:bookworm-slim
ARG BASHUNIT_VERSION=0.50.1
RUN apt-get update \
 && apt-get install -y --no-install-recommends bash zsh git ripgrep shellcheck jq iproute2 \
      ca-certificates curl tar gzip python3 php-cli procps \
 && curl -fsSL "https://github.com/TypedDevs/bashunit/releases/download/$BASHUNIT_VERSION/bashunit" \
      -o /usr/local/bin/bashunit \
 && chmod +x /usr/local/bin/bashunit \
 && rm -rf /var/lib/apt/lists/*
