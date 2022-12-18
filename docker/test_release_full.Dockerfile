ARG BASE_IMAGE
FROM $BASE_IMAGE

COPY . /test

ARG BIN_NAME
ARG TEST_ARGS

RUN \
  cd /test && \
  ls -la . && \
  chmod +x $BIN_NAME && \
  ./$BIN_NAME TEST_ARGS
