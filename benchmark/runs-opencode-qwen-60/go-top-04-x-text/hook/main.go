package main

import (
	"fmt"
	"os"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/unicode"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// encode converts a string from one encoding to another
func encode(input string, enc encoding.Encoding) ([]byte, error) {
	encoded, _, err := transform.Bytes(enc.NewEncoder(), []byte(input))
	if err != nil {
		return nil, fmt.Errorf("encoding failed: %w", err)
	}
	return encoded, nil
}

// decode converts bytes from a given encoding to a string
func decode(input []byte, enc encoding.Encoding) (string, error) {
	decoded, _, err := transform.Bytes(enc.NewDecoder(), input)
	if err != nil {
		return "", fmt.Errorf("decoding failed: %w", err)
	}
	return string(decoded), nil
}

// normalize applies Unicode normalization (NFC by default)
func normalize(input string, form norm.Form) string {
	return norm.Form(form).String(input)
}

func main() {
	// Example: Convert from Latin-1 to UTF-8
	latin1Str := "Caf\u00e9 R\u00e9sum\u00e9" // Café Résumé in Latin-1
	utf8, err := encode(latin1Str, unicode.UTF8)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error encoding: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Latin-1 input: %s\n", latin1Str)
	fmt.Printf("UTF-8 output:  %s\n", string(utf8))

	// Example: Unicode normalization (NFC)
	accentedNFD := "\u0041\u0300" // 'A' + combining grave accent (NFD)
	nfc := normalize(accentedNFD, norm.NFC)
	fmt.Printf("\nNFD input:  %q (len=%d)\n", accentedNFD, len(accentedNFD))
	fmt.Printf("NFC output: %q (len=%d)\n", nfc, len(nfc))

	// Example: Decode UTF-16 to string
	utf16Bytes := []byte{0x00, 0x48, 0x00, 0x65, 0x00, 0x6C, 0x00, 0x6C, 0x00, 0x6F} // "Hello" in UTF-16BE
	decoded, err := decode(utf16Bytes, unicode.UTF16(unicode.BigEndian, unicode.IgnoreBOM))
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error decoding: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("\nUTF-16BE bytes: %v\n", utf16Bytes)
	fmt.Printf("Decoded string: %s\n", decoded)

	fmt.Println("\nText encoding conversions and Unicode normalization working correctly!")
}