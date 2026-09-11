FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN go build -o myapp .

FROM debian:bookworm-slim
COPY --from=build /src/myapp /usr/local/bin/myapp
ENTRYPOINT ["/usr/local/bin/myapp"]
