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
	r := transform.NewReader(strings.NewReader(string(latin1)), charmap.ISO8859_1.NewDecoder())
	out, err := io.ReadAll(r)
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func main() {
	utf8Str, err := toUTF8([]byte("caf\xe9"))
	if err != nil {
		panic(err)
	}
	fmt.Println("decoded:", utf8Str)

	composed := norm.NFC.String("café")
	decomposed := norm.NFD.String("café")
	fmt.Println("NFC:", composed, len(composed))
	fmt.Println("NFD:", decomposed, len(decomposed))
}
