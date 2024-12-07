FROM ubuntu:22.04

USER root

RUN apt-get update \
    && apt-get install -y python3 python-is-python3 python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install pillow pyyaml requests

# RUN mkdir -p /opt/nuclio/common/mymodels/

# COPY main.py model_handler.py /opt/nuclio/common/mymodels/

