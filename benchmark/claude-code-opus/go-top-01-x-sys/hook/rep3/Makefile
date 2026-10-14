PLATFORMS := linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64 windows/arm64

.PHONY: build test vet cross
build:
	go build -o bin/syscli ./cmd/syscli

test:
	go test ./...

vet:
	@for p in $(PLATFORMS); do \
		echo "vet $$p"; GOOS=$${p%/*} GOARCH=$${p#*/} go vet ./... || exit 1; \
	done

cross:
	@for p in $(PLATFORMS); do \
		os=$${p%/*}; arch=$${p#*/}; ext=; [ $$os = windows ] && ext=.exe; \
		echo "build $$p"; \
		CGO_ENABLED=0 GOOS=$$os GOARCH=$$arch go build -o bin/syscli-$$os-$$arch$$ext ./cmd/syscli || exit 1; \
	done
