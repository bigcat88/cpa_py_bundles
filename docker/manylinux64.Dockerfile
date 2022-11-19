FROM quay.io/pypa/manylinux2014_aarch64

RUN \
  yum install wget openssl11-devel -y && \
  mkdir /usr/local/openssl11 && \
  cd /usr/local/openssl11 && \
  ln -s /usr/lib64/openssl11 lib && \
  ln -s /usr/include/openssl11 include && \
  cd / && \
  yum install libffi-devel -y && \
  wget https://www.python.org/ftp/python/3.9.15/Python-3.9.15.tgz && \
  tar xvf Python-3.9.15.tgz && \
  cd Python-3.9.15 && \
  ./configure --with-openssl=/usr/local/openssl11 --enable-optimizations && \
  make install && \
  python3 -m pip install --upgrade pip && \
  python3 -m pip install --upgrade setuptools
