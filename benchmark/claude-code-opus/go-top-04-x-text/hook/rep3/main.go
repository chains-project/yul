package main

import (
	"fmt"
	"log"

	"example.com/textconv/textutil"
	"golang.org/x/text/unicode/norm"
)

func main() {
	s, err := textutil.DecodeToUTF8([]byte{0x63, 0x61, 0x66, 0xe9}, "windows-1252")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("decoded: %s\n", s)
	fmt.Printf("NFD bytes: % x\n", textutil.Normalize(s, norm.NFD))
}
