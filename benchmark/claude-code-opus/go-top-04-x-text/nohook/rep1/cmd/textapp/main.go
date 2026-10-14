// Command textapp converts text between encodings and normalizes it.
//
//	textapp -from windows-1252 -to utf-8 -norm NFC < in.txt > out.txt
package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"

	"example.com/textapp/internal/textutil"
)

func main() {
	from := flag.String("from", "utf-8", "input encoding (WHATWG label)")
	to := flag.String("to", "utf-8", "output encoding (WHATWG label)")
	form := flag.String("norm", "NFC", "normalization form: NFC, NFD, NFKC, NFKD")
	flag.Parse()

	f, err := textutil.ParseForm(*form)
	if err != nil {
		fatal(err)
	}
	w := bufio.NewWriter(os.Stdout)
	if err := textutil.Convert(w, os.Stdin, *from, *to, f); err != nil {
		fatal(err)
	}
	if err := w.Flush(); err != nil {
		fatal(err)
	}
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "textapp:", err)
	os.Exit(1)
}
