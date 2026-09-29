package main

import (
	"fmt"
	"os"

	"textconv/internal/textconv"

	"golang.org/x/text/unicode/norm"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

func run() error {
	// "Café" in windows-1252.
	src := []byte{0x43, 0x61, 0x66, 0xE9}

	utf8, err := textconv.Decode("windows-1252", src)
	if err != nil {
		return err
	}

	// Normalize to NFC so combining marks are composed.
	nfc := textconv.Normalize(norm.NFC, string(utf8))

	fmt.Printf("decoded: %s\n", utf8)
	fmt.Printf("nfc:     %s\n", nfc)

	back, err := textconv.Encode("windows-1252", []byte(nfc))
	if err != nil {
		return err
	}
	fmt.Printf("encoded: % x\n", back)
	return nil
}
