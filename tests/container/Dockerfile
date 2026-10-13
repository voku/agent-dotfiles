# Local mirror of the Linux CI job: Bash, Zsh, ShellCheck, Git, ripgrep, jq, ss.
FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends bash zsh git ripgrep shellcheck jq iproute2 \
      ca-certificates curl tar gzip python3 php-cli procps \
 && rm -rf /var/lib/apt/lists/* \
 && git config --system --add safe.directory '*'
