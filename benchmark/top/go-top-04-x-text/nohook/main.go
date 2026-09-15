package main

import (
	"fmt"
	"io"
	"strings"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// toUTF8 decodes bytes in the given legacy encoding into a UTF-8 string.
func toUTF8(b []byte, enc *charmap.Charmap) (string, error) {
	r := transform.NewReader(strings.NewReader(string(b)), enc.NewDecoder())
	out, err := io.ReadAll(r)
	if err != nil {
		return "", err
	}
	return string(out), nil
}

// fromUTF8 encodes a UTF-8 string into the given legacy encoding.
func fromUTF8(s string, enc *charmap.Charmap) ([]byte, error) {
	r := transform.NewReader(strings.NewReader(s), enc.NewEncoder())
	return io.ReadAll(r)
}

func main() {
	// Windows-1252 -> UTF-8
	win1252 := []byte{0x93, 'H', 'e', 'l', 'l', 'o', 0x94, ' ', 0xE9} // “Hello” é
	utf8Str, err := toUTF8(win1252, charmap.Windows1252)
	if err != nil {
		fmt.Println("decode error:", err)
		return
	}
	fmt.Printf("Decoded from Windows-1252: %q\n", utf8Str)

	// UTF-8 -> ISO-8859-1
	latin1, err := fromUTF8("café", charmap.ISO8859_1)
	if err != nil {
		fmt.Println("encode error:", err)
		return
	}
	fmt.Printf("Encoded to ISO-8859-1: % X\n", latin1)

	// Unicode normalization: compare NFC vs NFD forms of the same text.
	composed := "é"                // U+00E9 (single code point, NFC)
	decomposed := "é"        // "e" + combining acute accent (NFD)
	fmt.Printf("composed == decomposed: %v\n", composed == decomposed)
	fmt.Printf("NFC-normalized equal: %v\n", norm.NFC.String(composed) == norm.NFC.String(decomposed))
	fmt.Printf("NFKC form: %q\n", norm.NFKC.String(decomposed))
}
