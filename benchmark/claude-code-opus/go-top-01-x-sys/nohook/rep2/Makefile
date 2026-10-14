PLATFORMS := linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64 windows/arm64

.PHONY: build test vet cross clean

build:
	go build -o bin/systool ./cmd/systool

test:
	go test ./...

# Vet every target OS: catches build-tag and type mismatches without needing each OS.
vet:
	@for p in $(PLATFORMS); do \
		echo "vet $$p"; \
		GOOS=$${p%/*} GOARCH=$${p#*/} go vet ./... || exit 1; \
	done

cross:
	@for p in $(PLATFORMS); do \
		os=$${p%/*}; arch=$${p#*/}; ext=; [ $$os = windows ] && ext=.exe; \
		echo "build $$p"; \
		CGO_ENABLED=0 GOOS=$$os GOARCH=$$arch go build -o bin/systool-$$os-$$arch$$ext ./cmd/systool || exit 1; \
	done

clean:
	rm -rf bin
