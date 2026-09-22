FROM --platform=$BUILDPLATFORM alpine:3.20
ARG TARGETPLATFORM
ARG BUILDPLATFORM
RUN echo "Building for $TARGETPLATFORM on $BUILDPLATFORM"
CMD ["sh", "-c", "echo hello from multi-platform image"]
