package main

import (
	"fmt"
	"io"
	"log"
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
	original := []byte("Caf\xe9") // "Café" in Latin-1
	utf8Str, err := toUTF8(original)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Latin-1 -> UTF-8: %q\n", utf8Str)

	roundTrip, err := fromUTF8(utf8Str)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("UTF-8 -> Latin-1: %v\n", roundTrip)

	nfc := norm.NFC.String("é") // "e" + combining acute accent
	nfd := norm.NFD.String(nfc)
	fmt.Printf("NFC: %q (len %d)\n", nfc, len(nfc))
	fmt.Printf("NFD: %q (len %d)\n", nfd, len(nfd))
	fmt.Printf("NFC-normalized equal: %v\n", norm.NFC.String("café") == norm.NFC.String("café"))
}
