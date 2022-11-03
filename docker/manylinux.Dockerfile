FROM debian:buster-slim

RUN \
  apt-get update && \
  apt-get install -y \
    git \
    build-essential \
    autoconf \
    automake \
    zlib1g-dev \
    libssl-dev \
    libreadline-dev \
    liblzma-dev \
    libbz2-dev \
    uuid-dev \
    libffi-dev \
    wget && \
  echo "**** Installing Cmake ****" && \
  wget https://github.com/Kitware/CMake/releases/download/v3.23.5/cmake-3.23.5.tar.gz && \
  tar -xf cmake-3.23.5.tar.gz && cd cmake-3.23.5 && \
  ./bootstrap && make && make install && \
  echo "**** Installing Patchelf ****" && \
  git clone https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make install && \
  echo "**** Installing Python ****" && \
  wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz && \
  tar -xf Python-3.9.0.tgz && cd Python-3.9.0 && \
  ./configure --enable-optimizations && make -j 4 && \
  make install && cd .. && . ~/.profile && \
  python3 -m pip install --upgrade pip
