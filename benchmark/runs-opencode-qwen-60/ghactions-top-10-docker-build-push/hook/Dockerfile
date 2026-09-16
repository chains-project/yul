FROM golang:1.23-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o myapp .

FROM alpine:3.20

COPY --from=builder /app/myapp /myapp

ENTRYPOINT ["/myapp"]