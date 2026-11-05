# syntax=docker/dockerfile:1

# Base image pinned by tag AND digest in both FROM lines. The tag is for humans;
# the digest is what Docker actually pulls, so the build can't silently change if
# the tag is moved. Dependabot opens a PR when a newer digest is published (it
# reads FROM lines directly, which is why this isn't factored into an ARG).

# ---------------------------------------------------------------- stage 1: build
# Builds a wheel. Build tooling (setuptools, pip caches, source tree) stays in
# this stage and never reaches the final image.
FROM python:3.15.0-slim-trixie@sha256:f5b92f2a669a4c347044f29367f31983280b648250ca94dea66f98c53bc87e58 AS build

WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /dist .

# ---------------------------------------------------------------- stage 2: runtime
FROM python:3.15.0-slim-trixie@sha256:f5b92f2a669a4c347044f29367f31983280b648250ca94dea66f98c53bc87e58 AS runtime

LABEL org.opencontainers.image.title="pwcheck" \
      org.opencontainers.image.description="Password strength checker with HaveIBeenPwned k-anonymity breach lookup" \
      org.opencontainers.image.source="https://github.com/DGUY1-wilm/pwcheck" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dedicated unprivileged user with a fixed UID, no home directory and no login shell.
RUN groupadd --system --gid 10001 pwcheck \
 && useradd --system --uid 10001 --gid pwcheck --no-create-home \
            --shell /usr/sbin/nologin pwcheck

# Install the wheel, then remove pip itself: the app never installs anything at
# runtime, and every tool left in the image is attack surface (and CVE noise).
COPY --from=build /dist/*.whl /tmp/
RUN python -m pip install --no-cache-dir /tmp/*.whl \
 && rm -f /tmp/*.whl \
 && python -m pip uninstall --yes pip

# Numeric UID so Kubernetes "runAsNonRoot" can verify it without reading /etc/passwd.
USER 10001:10001

ENTRYPOINT ["pwcheck"]
