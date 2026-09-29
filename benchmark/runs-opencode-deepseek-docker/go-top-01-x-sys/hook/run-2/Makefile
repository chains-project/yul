BIN := syscallkit

.PHONY: all build test tidy vet cross clean

all: build

build:
	go build -o bin/$(BIN) .

test:
	go test ./...

vet:
	go vet ./...

tidy:
	go mod tidy

cross:
	GOOS=linux   GOARCH=amd64 go build -o bin/$(BIN)-linux-amd64 .
	GOOS=linux   GOARCH=arm64 go build -o bin/$(BIN)-linux-arm64 .
	GOOS=darwin  GOARCH=amd64 go build -o bin/$(BIN)-darwin-amd64 .
	GOOS=darwin  GOARCH=arm64 go build -o bin/$(BIN)-darwin-arm64 .
	GOOS=windows GOARCH=amd64 go build -o bin/$(BIN)-windows-amd64.exe .
	GOOS=windows GOARCH=arm64 go build -o bin/$(BIN)-windows-arm64.exe .

clean:
	rm -rf bin
