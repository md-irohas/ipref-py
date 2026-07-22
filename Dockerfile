# syntax=docker/dockerfile:1

############################################################################
# ipref container image (web interface)
#
#   This image runs the ipref web interface with gunicorn.
#
#   For a quick trial, it bundles MaxMind's sample test databases (from
#   tests/data/) and a demo config (ipref/config.yaml.orig) so it works out of
#   the box:
#
#     docker build -t ipref .
#     docker run --rm -p 8000:8000 ipref   # open http://127.0.0.1:8000/
#
#   NOTE: the bundled databases are MaxMind's small SAMPLE data for testing
#   only. For real look-ups, mount your own config and databases and point
#   IPREF_CONF at the config:
#
#     docker run --rm -p 8000:8000 \
#       -v /path/to/config.yaml:/app/config.yaml:ro \
#       -v /path/to/dbs:/app/data:ro \
#       -e IPREF_CONF=/app/config.yaml \
#       ipref
############################################################################

# ---- Builder: build the wheel with uv ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /src
COPY . .

RUN uv build --wheel --out-dir /dist

# ---- Runtime: install the wheel and run gunicorn ----
FROM python:3.12-slim AS runtime

# Run as a non-root user.
RUN useradd --create-home --uid 1000 ipref

# Install ipref with the web extra from the built wheel.
COPY --from=builder /dist/*.whl /tmp/
RUN wheel="$(ls /tmp/*.whl)" && \
    pip install --no-cache-dir "${wheel}[web]" && \
    rm -f /tmp/*.whl

# Bundle MaxMind's sample test databases and a demo config so the image works
# out of the box. The demo config uses paths relative to this workdir
# (tests/data/...), so gunicorn must run from here. Demo data only.
WORKDIR /app
COPY tests/data/*.mmdb /app/tests/data/
COPY ipref/config.yaml.orig /app/config.yaml

USER ipref

# Path to the config file. Defaults to the bundled demo config; override with a
# mounted file for real look-ups.
ENV IPREF_CONF=/app/config.yaml

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ipref.web:create_app()"]
