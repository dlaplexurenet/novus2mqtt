# syntax=docker/dockerfile:1

FROM python:3.11-slim AS build

WORKDIR /novus2mqtt

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libffi-dev bash && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    apt-get remove --purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY config /novus2mqtt/config
COPY main.py /novus2mqtt
COPY run.sh /novus2mqtt
COPY healthcheck.sh /novus2mqtt
RUN chmod +x /novus2mqtt/run.sh /novus2mqtt/healthcheck.sh

# Add user and ensure they are in the dialout group
RUN useradd -ms /bin/bash paulnovus && usermod -aG dialout paulnovus

USER paulnovus

# Ensure PYTHONPATH is defined
ENV PYTHONPATH=""
ENV PYTHONPATH="/novus2mqtt:${PYTHONPATH:-}"

CMD ["/novus2mqtt/run.sh"]
