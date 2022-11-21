ARG BUILD_IMG
FROM $BUILD_IMG as base

ARG BASE_INIT_1
COPY ./$BASE_INIT_1 /install_python.sh
RUN \
  /install_python.sh && \
  rm /install_python.sh

ARG BASE_INIT_2
COPY ./$BASE_INIT_2 /install_other.sh
RUN \
  /install_other.sh && \
  rm /install_other.sh

RUN \
  python3 -m pip install --upgrade pip && \
  python3 -m pip install --upgrade setuptools wheel ordered-set && \
  python3 -m pip install --upgrade nuitka


FROM base as framework

# Here will be simple: ``python3 -m pip install nc_py_api==0.1.0`` in future
RUN \
  python3 -m pip install --upgrade pg8000 pymysql


FROM framework as release

COPY ./python/requirements.txt /

RUN \
  python3 -m pip install -r requirements.txt && \
  rm /requirements.txt


FROM release as binaries

COPY . /build

RUN \
  cd build && \
  python3 -m nuitka --plugin-enable=numpy --standalone --onefile ./python/main.py && \
  cp main.bin /main.bin && \
  cd / && \
  rm -rf /build
