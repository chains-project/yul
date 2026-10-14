// Package textutil provides helpers for character-set conversion and
// Unicode normalization.
package textutil

import (
	"fmt"
	"io"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// Lookup returns the encoding for a WHATWG/IANA name such as
// "utf-8", "shift_jis", "windows-1252" or "iso-8859-1".
func Lookup(name string) (encoding.Encoding, error) {
	enc, err := htmlindex.Get(name)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q: %w", name, err)
	}
	return enc, nil
}

// DecodeToUTF8 converts b from the named encoding to UTF-8.
func DecodeToUTF8(b []byte, from string) (string, error) {
	enc, err := Lookup(from)
	if err != nil {
		return "", err
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), b)
	return string(out), err
}

// EncodeFromUTF8 converts UTF-8 s to the named encoding. Characters that
// cannot be represented cause an error.
func EncodeFromUTF8(s, to string) ([]byte, error) {
	enc, err := Lookup(to)
	if err != nil {
		return nil, err
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), []byte(s))
	return out, err
}

// NewDecodingReader wraps r so that reads yield UTF-8 decoded from the
// named encoding. Use this for large inputs instead of DecodeToUTF8.
func NewDecodingReader(r io.Reader, from string) (io.Reader, error) {
	enc, err := Lookup(from)
	if err != nil {
		return nil, err
	}
	return transform.NewReader(r, enc.NewDecoder()), nil
}

// Normalize returns s in the given Unicode normalization form
// (norm.NFC, norm.NFD, norm.NFKC or norm.NFKD).
func Normalize(s string, form norm.Form) string {
	return form.String(s)
}

// Equal reports whether a and b are canonically equivalent, i.e. equal
// after NFC normalization.
func Equal(a, b string) bool {
	return norm.NFC.String(a) == norm.NFC.String(b)
}
