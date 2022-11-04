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
    python3-pip && \
  echo "**** Installing Patchelf ****" && \
  git clone https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make install && \
  cd .. && \
  python3 -m pip install --upgrade pip
