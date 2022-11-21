FROM debian:11

RUN \
  apt-get update && \
  apt-get install -y \
    git \
    build-essential \
    autoconf \
    automake \
    libffi-dev \
    wget \
    cmake \
    python3-pip \
    python3-dev \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    pkg-config \
    zlib1g-dev \
    libjpeg62-turbo-dev \
    liblcms2-dev \
    libwebp-dev \
    libfribidi-dev \
    libharfbuzz-dev && \
  echo "**** Installing Patchelf ****" && \
  git clone -b 0.17.0 https://github.com/NixOS/patchelf.git && \
  pushd patchelf && \
  ./bootstrap.sh && ./configure && make && make check && make install && \
  popd

RUN \
  python3 -m pip install --upgrade pip && \
  python3 -m pip install --upgrade setuptools && \
  python3 -m pip install --upgrade wheel ordered-set nuitka
