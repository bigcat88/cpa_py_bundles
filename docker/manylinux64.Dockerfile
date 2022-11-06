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
  cat /etc/os-release && uname -a && \
  echo "**** Installing Patchelf ****" && \
  git https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make check || true && \
  cat tests/replace-add-needed.sh.log && echo "***" && \
  cat tests/set-interpreter-long.sh.log
#    && make install && \
#  cd .. && \
#  python3 -m pip install --upgrade pip
