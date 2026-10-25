# syntax=docker/dockerfile:1
# Local mirror of the Linux CI job: Bash, Zsh, ShellCheck, Git, ripgrep, jq, ss.
FROM debian:bookworm-slim
ARG BASHUNIT_VERSION=0.50.1
ARG BASHUNIT_SHA256=18d83d590c5304f1853dd4fe4fec4ec6effbd9fe5a21831fe9f66f70afe17d93
RUN --mount=type=secret,id=proxy_ca,required=false \
    set -eu; \
    apt-get update; \
    apt-get install -y --no-install-recommends bash zsh git ripgrep shellcheck jq iproute2 unzip \
        ca-certificates curl tar gzip python3 php-cli procps; \
    if [ -s /run/secrets/proxy_ca ]; then \
        cat /etc/ssl/certs/ca-certificates.crt /run/secrets/proxy_ca > /tmp/agent-dotfiles-ca.pem; \
        curl --cacert /tmp/agent-dotfiles-ca.pem -fsSL \
            "https://github.com/TypedDevs/bashunit/releases/download/$BASHUNIT_VERSION/bashunit" \
            -o /usr/local/bin/bashunit; \
    else \
        curl -fsSL "https://github.com/TypedDevs/bashunit/releases/download/$BASHUNIT_VERSION/bashunit" \
            -o /usr/local/bin/bashunit; \
    fi; \
    echo "$BASHUNIT_SHA256  /usr/local/bin/bashunit" | sha256sum -c -; \
    chmod +x /usr/local/bin/bashunit; \
    rm -f /tmp/agent-dotfiles-ca.pem; \
    rm -rf /var/lib/apt/lists/*
