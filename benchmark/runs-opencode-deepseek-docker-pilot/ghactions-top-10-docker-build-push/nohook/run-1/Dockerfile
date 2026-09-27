FROM golang:alpine AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /myapp .

FROM alpine:latest
COPY --from=build /myapp /myapp
ENTRYPOINT ["/myapp"]
