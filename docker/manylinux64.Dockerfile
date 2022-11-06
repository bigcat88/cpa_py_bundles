FROM almalinux:8.6

RUN \
  dnf update -y && \
  dnf install -y \
    git \
    autoconf \
    automake \
    gcc \
    gcc-c++ && \
  echo "**** Installing Patchelf ****" && \
  git clone -b 0.16.1 https://github.com/NixOS/patchelf.git && \
  cd patchelf && \
  ./bootstrap.sh && ./configure && make && make check || true && \
  cat tests/replace-add-needed.sh.log && echo "***" && \
  cat tests/set-interpreter-long.sh.log && cat /etc/os-release && uname -a
#    && make install && \
#  cd .. && \
#  python3 -m pip install --upgrade pip
