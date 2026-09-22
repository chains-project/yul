FROM --platform=$BUILDPLATFORM alpine:3.20 AS build
ARG TARGETPLATFORM
RUN echo "Building for $TARGETPLATFORM" > /out.txt

FROM alpine:3.20
COPY --from=build /out.txt /out.txt
CMD ["cat", "/out.txt"]
