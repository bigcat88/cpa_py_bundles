#FROM ghcr.io/linuxserver/baseimage-alpine:3.14
#
#COPY .. /nuitka_testing
#
#RUN \
#  apk add --no-cache \
#    py3-pip \
#    python3-dev \
#    libtool \
#    git \
#    gcc \
#    m4 \
#    perl \
#    alpine-sdk \
#    cmake \
#    fribidi-dev \
#    harfbuzz-dev \
#    jpeg-dev \
#    lcms2-dev \
#    openjpeg-dev \
#    nasm \
#    libde265-dev \
#    py3-numpy \
#    py3-pillow && \
#  python3 -m pip install --upgrade pip
