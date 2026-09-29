package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/encoding/japanese"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

var encodings = map[string]encoding.Encoding{
	"utf-8":       nil,
	"utf8":        nil,
	"windows1252": charmap.Windows1252,
	"cp1252":      charmap.Windows1252,
	"latin1":      charmap.ISO8859_1,
	"iso8859-1":   charmap.ISO8859_1,
	"shiftjis":    japanese.ShiftJIS,
	"sjis":        japanese.ShiftJIS,
}

func main() {
	from := flag.String("from", "utf-8", "source encoding")
	to := flag.String("to", "utf-8", "target encoding")
	form := flag.String("norm", "nfc", "Unicode normalization form: nfc, nfd, nfkc, nfkd, or none")
	flag.Parse()

	if err := run(*from, *to, *form, os.Stdin, os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, "textconv:", err)
		os.Exit(1)
	}
}

func run(from, to, form string, in io.Reader, out io.Writer) error {
	if from == "" {
		from = "utf-8"
	}
	if to == "" {
		to = "utf-8"
	}
	src, ok := encodings[from]
	if !ok {
		return fmt.Errorf("unknown source encoding %q", from)
	}
	dst, ok := encodings[to]
	if !ok {
		return fmt.Errorf("unknown target encoding %q", to)
	}

	dec, err := newDecoder(src)
	if err != nil {
		return err
	}
	enc, err := newEncoder(dst)
	if err != nil {
		return err
	}
	normalizer, err := newNormalizer(form)
	if err != nil {
		return err
	}

	chain := transform.Chain(dec, normalizer, enc)
	_, err = io.Copy(out, transform.NewReader(in, chain))
	return err
}

func newDecoder(e encoding.Encoding) (transform.Transformer, error) {
	if e == nil {
		return transform.Nop, nil
	}
	return e.NewDecoder(), nil
}

func newEncoder(e encoding.Encoding) (transform.Transformer, error) {
	if e == nil {
		return transform.Nop, nil
	}
	return e.NewEncoder(), nil
}

func newNormalizer(form string) (transform.Transformer, error) {
	switch form {
	case "", "none":
		return transform.Nop, nil
	case "nfc":
		return norm.NFC, nil
	case "nfd":
		return norm.NFD, nil
	case "nfkc":
		return norm.NFKC, nil
	case "nfkd":
		return norm.NFKD, nil
	default:
		return nil, fmt.Errorf("unknown normalization form %q", form)
	}
}
