FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN go build -o myapp .

FROM gcr.io/distroless/base-debian12
COPY --from=build /src/myapp /usr/local/bin/myapp
ENTRYPOINT ["myapp"]
