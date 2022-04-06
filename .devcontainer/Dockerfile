# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.231.3/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# install requirements for build
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get dist-upgrade -y \
    && apt-get -y install \
        libocct-* \
        occt-misc \
        git \
        automake \
        bison \
        build-essential \
        cmake \
        swig \
        libboost-dev \
        libgl1-mesa-dev \
        libglu1-mesa-dev \
        libharfbuzz-dev \
        libpcre3-dev \
        libtbb-dev \
        libxi-dev \
        rapidjson-dev \
        mesa-utils \
        xserver-xorg-video-all \
        libqt5gui5 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxkbcommon-x11-0 \
        libdbus-1-3 \
        x11-apps

WORKDIR /tmp/build

COPY .devcontainer/*.patch /tmp/build/
COPY .devcontainer/build_pythonocc.sh /tmp/build/

RUN chmod +x *.sh

RUN ./build_pythonocc.sh 7.5.1

WORKDIR /

# clean out uneccesary build programs
RUN apt-get auto-remove -y \
        automake \
        bison \
        build-essential \
        cmake \
        swig \
        libboost-dev \
        libgl1-mesa-dev \
        libglu1-mesa-dev \
        libharfbuzz-dev \
        libpcre3-dev \
        libtbb-dev \
        libxi-dev \
        rapidjson-dev \
        && \
    rm -rf /var/lib/apt/lists/*
