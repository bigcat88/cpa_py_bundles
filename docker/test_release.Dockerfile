FROM debian:buster-slim

COPY . /cpa

ARG CPA_NAME

RUN \
  cd /cpa && \
  ls -la . && \
  chmod +x $CPA_NAME && \
  ls -la . && \
  ./$CPA_NAME --version
