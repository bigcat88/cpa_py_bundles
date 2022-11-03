FROM almalinux:8.6

RUN \
  dnf update -y && \
  dnf install -y \
    python39-devel \
    git \
    cmake \
    autoconf \
    automake \
    gcc \
    gcc-c++ && \
  echo "**** Installing Patchelf ****" && \
  git clone https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make install && \
  python3 -m pip install --upgrade pip
