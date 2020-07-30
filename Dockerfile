# Dockerfile
#
# Specify the base image
FROM rootproject/root-conda:latest

# Build the image as root user
USER root

# set the non-interactive mode for apt-get
ENV DEBIAN_FRONTEND noninteractive

COPY . /home/docker/bucoffea

# Set the default working directory when a container is launched
WORKDIR /home/docker

# Run some bash commands to install packages
RUN pip install -e bucoffea

# Run container with user docker
USER docker

