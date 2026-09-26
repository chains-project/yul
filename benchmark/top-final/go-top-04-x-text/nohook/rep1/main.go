package main

import (
	"fmt"

	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/unicode/norm"
)

func main() {
	decoded, err := charmap.Windows1252.NewDecoder().String("Caf\xe9")
	if err != nil {
		panic(err)
	}
	fmt.Println("decoded:", decoded)

	normalized := norm.NFC.String("Café")
	fmt.Println("normalized:", normalized)
}
