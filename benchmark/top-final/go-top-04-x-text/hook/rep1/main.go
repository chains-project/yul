package main

import (
	"fmt"
	"io"
	"strings"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

func toUTF8(latin1 []byte) (string, error) {
	r := charmap.ISO8859_1.NewDecoder().Reader(strings.NewReader(string(latin1)))
	out, err := io.ReadAll(r)
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func fromUTF8(s string) ([]byte, error) {
	w := charmap.ISO8859_1.NewEncoder()
	out, _, err := transform.String(w, s)
	if err != nil {
		return nil, err
	}
	return []byte(out), nil
}

func main() {
	decoded, err := toUTF8([]byte("caf\xe9"))
	if err != nil {
		panic(err)
	}
	fmt.Println("decoded:", decoded)

	encoded, err := fromUTF8(decoded)
	if err != nil {
		panic(err)
	}
	fmt.Printf("re-encoded: %x\n", encoded)

	// Unicode normalization: NFC vs NFD.
	nfc := norm.NFC.String("café")
	nfd := norm.NFD.String("café")
	fmt.Printf("NFC bytes: %x\n", nfc)
	fmt.Printf("NFD bytes: %x\n", nfd)
	fmt.Println("NFC == NFD (normalized):", norm.NFC.String(nfd) == nfc)
}
