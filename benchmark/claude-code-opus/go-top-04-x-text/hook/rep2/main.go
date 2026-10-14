package main

import (
	"fmt"
	"log"

	"example.com/textapp/textutil"
)

func main() {
	s, err := textutil.DecodeToUTF8([]byte{0x63, 0x61, 0x66, 0xE9}, "windows-1252")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("decoded: %s\n", s)
	fmt.Printf("NFD length: %d bytes, NFC length: %d bytes\n",
		len(textutil.Normalize(s, textutil.NFD)), len(textutil.Normalize(s, textutil.NFC)))
}
