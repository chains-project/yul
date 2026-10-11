package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"textconv/internal/textcodec"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "textconv:", err)
		os.Exit(1)
	}
}

func run() error {
	fromName := flag.String("from", "utf-8", "source encoding (IANA/WHATWG name, e.g. utf-8, windows-1252, shift_jis)")
	toName := flag.String("to", "utf-8", "target encoding")
	formName := flag.String("norm", "", "Unicode normalization form: NFC, NFD, NFKC or NFKD (optional)")
	inPath := flag.String("in", "-", "input file, or - for stdin")
	outPath := flag.String("out", "-", "output file, or - for stdout")
	flag.Parse()

	from, err := textcodec.LookupEncoding(*fromName)
	if err != nil {
		return err
	}
	to, err := textcodec.LookupEncoding(*toName)
	if err != nil {
		return err
	}

	src, err := readAll(*inPath)
	if err != nil {
		return err
	}

	utf8, err := textcodec.Decode(src, from)
	if err != nil {
		return err
	}

	if *formName != "" {
		f, err := textcodec.LookupForm(*formName)
		if err != nil {
			return err
		}
		utf8 = []byte(textcodec.Normalize(string(utf8), &f))
	}

	out, err := textcodec.Encode(utf8, to)
	if err != nil {
		return err
	}

	return writeAll(*outPath, out)
}

func readAll(path string) ([]byte, error) {
	if path == "-" {
		return io.ReadAll(os.Stdin)
	}
	return os.ReadFile(path)
}

func writeAll(path string, data []byte) error {
	if path == "-" {
		_, err := os.Stdout.Write(data)
		return err
	}
	return os.WriteFile(path, data, 0o644)
}
