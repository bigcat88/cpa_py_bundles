ARG BUILD_IMG
FROM $BUILD_IMG as release

COPY ./python/requirements.txt /

RUN \
  python3 -m pip install -r requirements.txt && \
  rm requirements.txt


FROM release as binaries

COPY . /build

RUN \
  cd build && \
  python3 -m nuitka --plugin-enable=numpy --standalone --onefile ./python/main.py && \
  cp main.bin /main.bin && \
  cd / && \
  rm -rf /build
