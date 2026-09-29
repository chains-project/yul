GO ?= go
PKG ?= ./...

.PHONY: test test-verbose cover fmt vet tidy

test:
	$(GO) test $(PKG)

test-verbose:
	$(GO) test -v $(PKG)

cover:
	$(GO) test -coverprofile=coverage.out $(PKG)
	$(GO) tool cover -func=coverage.out

fmt:
	$(GO) fmt $(PKG)

vet:
	$(GO) vet $(PKG)

tidy:
	$(GO) mod tidy
