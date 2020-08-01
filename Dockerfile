# Dockerfile
#
# Specify the base image
FROM rootproject/root-conda:latest

# Build the image as root user
USER root

# Using bash as the default shell for RUN
SHELL ["/bin/bash", "-c"]

# set the non-interactive mode for apt-get
ENV DEBIAN_FRONTEND noninteractive

# Run some bash commands to install base packages
RUN source ~/.bashrc && \
	apt update && \
	apt install -y apt-utils && \
	apt install -y libcairo2-dev && \
	pip install pycairo

COPY . /bucoffea

# Set the default working directory when a container is launched
WORKDIR /bucoffea

# install bucoffea
RUN source ~/.bashrc && \
	pip install -e /bucoffea
