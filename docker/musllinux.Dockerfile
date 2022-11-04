FROM alpine:3.15

RUN \
  apk add --no-cache \
    py3-pip \
    python3-dev \
    libtool \
    git \
    gcc \
    m4 \
    perl \
    alpine-sdk \
    autoconf \
    automake \
    cmake \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    openjpeg-dev \
    nasm \
    gfortran \
    openblas-dev \
    py3-scipy && \
  echo "**** Installing Patchelf ****" && \
  git clone https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make install && \
  cd .. && \
  python3 -m pip install --upgrade pip
