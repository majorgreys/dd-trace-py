ARG PYTHON_VERSION=3.9-slim-buster

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION}

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # Translations dependencies
  gettext \
  # other dependencies
  procps \
  curl \
  # dependencies for installing Python packages from git
  build-essential \
  git \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Install sirun
# sirun
RUN curl -sL https://github.com/DataDog/sirun/releases/download/v0.1.8/sirun-v0.1.8-x86_64-unknown-linux-gnu.tar.gz | tar zxf - -C /tmp && mv /tmp/sirun /usr/bin

# k6
RUN curl -SL https://github.com/k6io/k6/releases/download/v0.32.0/k6-v0.32.0-linux-amd64.tar.gz | tar zxf - -C /tmp && mv /tmp/k6-v0.32.0-linux-amd64/k6 /usr/bin

# jq
RUN curl -L -o /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && \
  chmod +x /usr/bin/jq

# Create venv
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY encoder ${APP_HOME}
# FIXME: this should be in a common folder for all images
COPY django_simple/util.jq ${APP_HOME}

RUN pip install datadog==0.41.0

# For performance testing
ENV DDTRACE_GIT_COMMIT_ID ""
ENV DDTRACE_WHEELS ""
ENV SIRUN_NO_STDIO 0
ENV K6_STATSD_ENABLE_TAGS "true"

ENTRYPOINT ["/app/entrypoint"]
CMD ["/app/benchmark"]
