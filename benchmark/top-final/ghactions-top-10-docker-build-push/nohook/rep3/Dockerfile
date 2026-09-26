FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/myapp .

FROM gcr.io/distroless/static-debian12
COPY --from=build /out/myapp /myapp
ENTRYPOINT ["/myapp"]
