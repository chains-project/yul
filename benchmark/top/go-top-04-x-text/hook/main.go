package main

import (
	"fmt"
	"io"
	"os"
	"strings"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// toUTF8FromLatin1 converts Latin-1 (ISO-8859-1) encoded bytes to UTF-8.
func toUTF8FromLatin1(b []byte) (string, error) {
	out, _, err := transform.String(charmap.ISO8859_1.NewDecoder(), string(b))
	if err != nil {
		return "", err
	}
	return out, nil
}

// fromUTF8ToLatin1 converts a UTF-8 string to Latin-1 (ISO-8859-1) encoded bytes.
func fromUTF8ToLatin1(s string) ([]byte, error) {
	out, _, err := transform.String(charmap.ISO8859_1.NewEncoder(), s)
	if err != nil {
		return nil, err
	}
	return []byte(out), nil
}

// normalizeNFC returns the NFC (canonical composition) normalized form of s.
func normalizeNFC(s string) string {
	return norm.NFC.String(s)
}

func main() {
	input, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error reading stdin:", err)
		os.Exit(1)
	}

	decoded, err := toUTF8FromLatin1(input)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error decoding latin-1:", err)
		os.Exit(1)
	}

	normalized := normalizeNFC(decoded)

	reencoded, err := fromUTF8ToLatin1(normalized)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error encoding latin-1:", err)
		os.Exit(1)
	}

	fmt.Println(strings.TrimSpace(normalized))
	os.Stdout.Write(reencoded)
}
