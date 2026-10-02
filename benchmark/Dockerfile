FROM node:22-trixie

# A toolchain for every benchmarked ecosystem (npm, git and curl come with
# the base image), so agents can query registries and generate lockfiles as
# on a dev machine. Containers run as the host uid with HOME=/tmp, so caches
# land under /tmp; the rust image's toolchain dirs are already world-writable.
COPY --from=rust:1-trixie /usr/local/rustup /usr/local/rustup
COPY --from=rust:1-trixie /usr/local/cargo /usr/local/cargo
COPY --from=golang:1-trixie /usr/local/go /usr/local/go
COPY --from=maven:3 /opt/java/openjdk /opt/java/openjdk
COPY --from=maven:3 /usr/share/maven /usr/share/maven
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV RUSTUP_HOME=/usr/local/rustup CARGO_HOME=/usr/local/cargo JAVA_HOME=/opt/java/openjdk \
    PATH=/usr/local/cargo/bin:/usr/local/go/bin:/opt/java/openjdk/bin:/usr/share/maven/bin:$PATH
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip python3-venv python-is-python3 gh \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code
# Fresh caches make first cargo/mvn/go runs slow; 5 min instead of the 2 min default.
ENV BASH_DEFAULT_TIMEOUT_MS=300000
USER node
