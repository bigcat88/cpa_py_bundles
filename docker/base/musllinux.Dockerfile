ARG BUILD_IMG
FROM $BUILD_IMG as base

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
  git clone -b 0.17.0 https://github.com/NixOS/patchelf.git && \
  pushd patchelf && \
  ./bootstrap.sh && ./configure && make && make check && make install && \
  popd
