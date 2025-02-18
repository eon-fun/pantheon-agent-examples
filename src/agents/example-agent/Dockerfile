ARG BASE_IMAGE=rayproject/ray:latest

FROM ${BASE_IMAGE}

# Install specific tools directly
# RUN pip install example-tool==0.0.1

# Set the working dir for the container to /serve_app
WORKDIR /serve_app

COPY entrypoint.py /serve_app/entrypoint.py
