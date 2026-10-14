package main

import (
	"fmt"
	"log"

	"textconv/textutil"

	"golang.org/x/text/unicode/norm"
)

func main() {
	latin1 := []byte{'c', 'a', 'f', 0xE9} // "café" in Windows-1252
	s, err := textutil.ToUTF8(latin1, "windows-1252")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("decoded:  %q\n", s)
	fmt.Printf("NFD:      %+q\n", textutil.Normalize(s, norm.NFD))
	fmt.Printf("NFC:      %+q\n", textutil.Normalize(s, norm.NFC))
}
