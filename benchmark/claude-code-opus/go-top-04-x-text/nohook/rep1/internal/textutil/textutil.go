// Package textutil provides helpers for character-encoding conversion and
// Unicode normalization.
package textutil

import (
	"fmt"
	"io"
	"strings"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// Form is a Unicode normalization form.
type Form = norm.Form

// Supported normalization forms.
const (
	NFC  = norm.NFC
	NFD  = norm.NFD
	NFKC = norm.NFKC
	NFKD = norm.NFKD
)

// ParseForm returns the normalization form for a name such as "NFC".
func ParseForm(name string) (Form, error) {
	switch strings.ToUpper(name) {
	case "NFC":
		return NFC, nil
	case "NFD":
		return NFD, nil
	case "NFKC":
		return NFKC, nil
	case "NFKD":
		return NFKD, nil
	}
	return 0, fmt.Errorf("unknown normalization form %q", name)
}

// Lookup returns the encoding for a WHATWG label such as "utf-8",
// "windows-1252", "shift_jis" or "iso-8859-1".
func Lookup(label string) (encoding.Encoding, error) {
	enc, err := htmlindex.Get(label)
	if err != nil {
		return nil, fmt.Errorf("unsupported encoding %q: %w", label, err)
	}
	return enc, nil
}

// Decode converts bytes in the named encoding to a UTF-8 string.
func Decode(b []byte, label string) (string, error) {
	enc, err := Lookup(label)
	if err != nil {
		return "", err
	}
	out, err := enc.NewDecoder().Bytes(b)
	if err != nil {
		return "", err
	}
	return string(out), nil
}

// Encode converts a UTF-8 string to bytes in the named encoding. Characters
// that cannot be represented cause an error.
func Encode(s, label string) ([]byte, error) {
	enc, err := Lookup(label)
	if err != nil {
		return nil, err
	}
	return enc.NewEncoder().Bytes([]byte(s))
}

// Normalize returns s in the given normalization form.
func Normalize(s string, f Form) string {
	return f.String(s)
}

// Convert streams r (in encoding from) to w (in encoding to), applying
// normalization form f to the intermediate UTF-8 text.
func Convert(w io.Writer, r io.Reader, from, to string, f Form) error {
	src, err := Lookup(from)
	if err != nil {
		return err
	}
	dst, err := Lookup(to)
	if err != nil {
		return err
	}
	t := transform.Chain(src.NewDecoder(), f, dst.NewEncoder())
	_, err = io.Copy(w, transform.NewReader(r, t))
	return err
}
