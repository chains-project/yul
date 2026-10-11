// Command textconv converts text between encodings and Unicode
// normalization forms, reading from stdin and writing to stdout.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"golang.org/x/text/unicode/norm"

	"textconv"
)

func main() {
	fromName := flag.String("from", "utf-8", "source encoding (e.g. utf-8, windows-1252, shift_jis)")
	toName := flag.String("to", "utf-8", "target encoding")
	formName := flag.String("form", "", "Unicode normalization form: nfc, nfd, nfkc or nfkd")
	flag.Parse()

	if err := run(*fromName, *toName, *formName, os.Stdin, os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, "textconv:", err)
		os.Exit(1)
	}
}

func run(fromName, toName, formName string, in io.Reader, out io.Writer) error {
	from, err := textconv.Lookup(fromName)
	if err != nil {
		return err
	}
	to, err := textconv.Lookup(toName)
	if err != nil {
		return err
	}
	form, err := parseForm(formName)
	if err != nil {
		return err
	}

	data, err := io.ReadAll(in)
	if err != nil {
		return err
	}

	text, err := textconv.Decode(data, from)
	if err != nil {
		return err
	}
	if form != nil {
		text = form.String(text)
	}

	encoded, err := textconv.Encode(text, to)
	if err != nil {
		return err
	}
	_, err = out.Write(encoded)
	return err
}

func parseForm(name string) (*norm.Form, error) {
	switch name {
	case "":
		return nil, nil
	case "nfc":
		f := norm.NFC
		return &f, nil
	case "nfd":
		f := norm.NFD
		return &f, nil
	case "nfkc":
		f := norm.NFKC
		return &f, nil
	case "nfkd":
		f := norm.NFKD
		return &f, nil
	default:
		return nil, fmt.Errorf("unknown normalization form %q", name)
	}
}
