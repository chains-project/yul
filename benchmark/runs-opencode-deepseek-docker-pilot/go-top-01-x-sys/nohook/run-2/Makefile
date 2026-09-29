BINARY  := sysprobe
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo dev)
LDFLAGS := -s -w -X main.version=$(VERSION)
DIST    := dist
PKG     := ./cmd/sysprobe

.PHONY: all build test tidy fmt vet clean cross

all: fmt vet test build

build:
	CGO_ENABLED=0 go build -trimpath -ldflags '$(LDFLAGS)' -o $(BINARY) $(PKG)

test:
	go test ./...

tidy:
	go mod tidy

fmt:
	gofmt -l -w .

vet:
	go vet ./...

cross:
	@mkdir -p $(DIST)
	CGO_ENABLED=0 GOOS=linux   GOARCH=amd64 go build -trimpath -ldflags '$(LDFLAGS)' -o $(DIST)/$(BINARY)-linux-amd64      $(PKG)
	CGO_ENABLED=0 GOOS=linux   GOARCH=arm64 go build -trimpath -ldflags '$(LDFLAGS)' -o $(DIST)/$(BINARY)-linux-arm64      $(PKG)
	CGO_ENABLED=0 GOOS=darwin  GOARCH=amd64 go build -trimpath -ldflags '$(LDFLAGS)' -o $(DIST)/$(BINARY)-darwin-amd64     $(PKG)
	CGO_ENABLED=0 GOOS=darwin  GOARCH=arm64 go build -trimpath -ldflags '$(LDFLAGS)' -o $(DIST)/$(BINARY)-darwin-arm64     $(PKG)
	CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -trimpath -ldflags '$(LDFLAGS)' -o $(DIST)/$(BINARY)-windows-amd64.exe $(PKG)
	CGO_ENABLED=0 GOOS=windows GOARCH=arm64 go build -trimpath -ldflags '$(LDFLAGS)' -o $(DIST)/$(BINARY)-windows-arm64.exe $(PKG)

clean:
	rm -rf $(BINARY) $(DIST)
