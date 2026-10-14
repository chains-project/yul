package main

import (
	"fmt"
	"log"

	"example.com/textapp/internal/textutil"
)

func main() {
	sjis, err := textutil.EncodeFromUTF8("こんにちは", "shift_jis")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Shift_JIS bytes: % x\n", sjis)

	s, err := textutil.DecodeToUTF8(sjis, "shift_jis")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Decoded:", s)

	decomposed := "é"
	fmt.Printf("NFC of %q: %q\n", decomposed, textutil.Normalize(decomposed, textutil.NFC))
}
