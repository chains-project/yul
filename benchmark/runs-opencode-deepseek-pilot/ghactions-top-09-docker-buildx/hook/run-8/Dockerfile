FROM alpine:3.20

RUN apk add --no-cache ca-certificates

WORKDIR /app
COPY . .

CMD ["sh", "-c", "echo multi-platform image"]
