FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /myapp .

FROM gcr.io/distroless/static-debian12
COPY --from=build /myapp /myapp
ENTRYPOINT ["/myapp"]
