FROM quay.io/pypa/manylinux_2_28_aarch64

RUN \
  dnf install -y \
    python39-devel && \
  python3 -m pip install --upgrade pip
