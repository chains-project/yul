GO      ?= go
BINARY  ?= syscallcli
CMD     := ./cmd/$(BINARY)
BIN     := bin
TARGETS := linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64 windows/arm64

.PHONY: build test vet cross clean

build:
	$(GO) build -o $(BIN)/$(BINARY) $(CMD)

test:
	$(GO) test ./...

vet:
	$(GO) vet ./...

# Pure-Go low-level calls, so every target builds from any host with cgo off.
cross:
	@mkdir -p $(BIN)
	@for t in $(TARGETS); do \
		os=$${t%/*}; arch=$${t#*/}; ext=""; \
		[ "$$os" = windows ] && ext=".exe"; \
		echo "building $$os/$$arch"; \
		CGO_ENABLED=0 GOOS=$$os GOARCH=$$arch $(GO) build -o $(BIN)/$(BINARY)-$$os-$$arch$$ext $(CMD) || exit 1; \
	done

clean:
	rm -rf $(BIN)
