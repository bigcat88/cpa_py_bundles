ARG BUILD_IMG
FROM $BUILD_IMG as base

RUN \
  yum -y install libffi-devel wget && \
  wget -q https://www.openssl.org/source/openssl-1.1.1s.tar.gz && \
  tar -xzf openssl-1.1.1s.tar.gz && \
  pushd openssl-1.1.1s && \
  ./config no-shared --prefix=/usr/local/ssl --openssldir=/usr/local/ssl && \
  make && make install_sw && \
  popd && \
  wget https://www.python.org/ftp/python/3.9.15/Python-3.9.15.tgz && \
  tar xvf Python-3.9.15.tgz && \
  pushd Python-3.9.15 && \
  ./configure --with-openssl=/usr/local/ssl --enable-optimizations && \
  make install && \
  popd

RUN \
  python3 -m pip install --upgrade pip && \
  python3 -m pip install --upgrade setuptools && \
  python3 -m pip install --upgrade wheel ordered-set nuitka


FROM base-manylinux:latest as prod

ARG REQ_LIST
RUN \
  python3 -m pip install $REQ_LIST
