FROM golang:1.22-alpine AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/myapp .

FROM alpine:3.20
COPY --from=build /out/myapp /usr/local/bin/myapp
ENTRYPOINT ["myapp"]
