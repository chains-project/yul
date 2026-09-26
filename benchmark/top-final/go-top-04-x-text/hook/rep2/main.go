package main

import (
	"fmt"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/unicode/norm"
)

func main() {
	nfc := norm.NFC.String("Café")
	fmt.Println("NFC:", nfc)

	encoded, err := charmap.ISO8859_1.NewEncoder().String(nfc)
	if err != nil {
		fmt.Println("encode error:", err)
		return
	}
	fmt.Printf("ISO-8859-1 bytes: %v\n", []byte(encoded))
}
