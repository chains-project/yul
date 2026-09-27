MINGW ?= $(HOME)/.local/llvm-mingw
TRIPLE := x86_64-pc-windows-gnu

export PATH := $(MINGW)/bin:$(PATH)

.PHONY: build release check clippy fmt clean

build:
	cargo build --target $(TRIPLE)

release:
	cargo build --target $(TRIPLE) --release

check:
	cargo check --target $(TRIPLE)

clippy:
	cargo clippy --target $(TRIPLE) -- -D warnings

fmt:
	cargo fmt

clean:
	cargo clean
