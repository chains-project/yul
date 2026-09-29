BINARY    := sysprobe
DIST      := dist
PLATFORMS := linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64 windows/arm64

.PHONY: build vet generate cross clean

build:
	go build -o $(BINARY) .

vet:
	go vet ./...

generate:
	go generate ./...

cross:
	@mkdir -p $(DIST)
	@for p in $(PLATFORMS); do \
		os=$${p%/*}; arch=$${p#*/}; \
		ext=""; [ "$$os" = windows ] && ext=".exe"; \
		out="$(DIST)/$(BINARY)-$$os-$$arch$$ext"; \
		echo "building $$out"; \
		GOOS=$$os GOARCH=$$arch go build -o $$out . || exit 1; \
	done

clean:
	rm -rf $(BINARY) $(DIST)
