// Command texttool converts text between character encodings and applies
// Unicode normalization.
package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

var (
	from = flag.String("from", "utf-8", "source encoding (e.g. utf-8, iso-8859-1, windows-1252, shift_jis)")
	to   = flag.String("to", "utf-8", "target encoding (e.g. utf-8, iso-8859-1, windows-1252, shift_jis)")
	form = flag.String("norm", "", "Unicode normalization form to apply after decoding: NFC, NFD, NFKC, NFKD (default: none)")
)

func main() {
	flag.Parse()

	input, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error reading stdin:", err)
		os.Exit(1)
	}

	decoded, err := decode(input, *from)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error decoding input:", err)
		os.Exit(1)
	}

	normalized, err := normalize(decoded, *form)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error normalizing input:", err)
		os.Exit(1)
	}

	encoded, err := encode(normalized, *to)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error encoding output:", err)
		os.Exit(1)
	}

	os.Stdout.Write(encoded)
}

func decode(b []byte, encName string) ([]byte, error) {
	enc, err := htmlindex.Get(encName)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q: %w", encName, err)
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), b)
	return out, err
}

func encode(b []byte, encName string) ([]byte, error) {
	enc, err := htmlindex.Get(encName)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q: %w", encName, err)
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), b)
	return out, err
}

func normalize(b []byte, formName string) ([]byte, error) {
	var f norm.Form
	switch formName {
	case "":
		return b, nil
	case "NFC":
		f = norm.NFC
	case "NFD":
		f = norm.NFD
	case "NFKC":
		f = norm.NFKC
	case "NFKD":
		f = norm.NFKD
	default:
		return nil, fmt.Errorf("unknown normalization form %q (want NFC, NFD, NFKC, or NFKD)", formName)
	}
	return f.Append(nil, b...), nil
}
