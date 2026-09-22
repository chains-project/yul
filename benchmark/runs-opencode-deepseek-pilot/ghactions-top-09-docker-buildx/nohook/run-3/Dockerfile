FROM alpine:3.20

ARG TARGETPLATFORM
RUN echo "Building for ${TARGETPLATFORM}"

CMD ["sh", "-c", "echo hello from $(uname -m)"]
