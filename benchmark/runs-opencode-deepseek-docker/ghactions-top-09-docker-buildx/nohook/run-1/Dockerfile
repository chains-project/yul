FROM --platform=$BUILDPLATFORM alpine:3.20
ARG TARGETPLATFORM
ARG BUILDPLATFORM
RUN echo "Building on ${BUILDPLATFORM} for ${TARGETPLATFORM}"
CMD ["sh", "-c", "echo hello from $(uname -m)"]
