// Package textconv provides helpers for converting between character
// encodings and normalizing Unicode text.
package textconv

import (
	"fmt"
	"io"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// Lookup returns the encoding for a name or label such as "utf-8",
// "latin1", "windows-1252", "shift_jis" or "gbk".
func Lookup(name string) (encoding.Encoding, error) {
	enc, err := htmlindex.Get(name)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q: %w", name, err)
	}
	return enc, nil
}

// Decode converts bytes in the named encoding to a UTF-8 string.
func Decode(b []byte, from string) (string, error) {
	enc, err := Lookup(from)
	if err != nil {
		return "", err
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), b)
	if err != nil {
		return "", err
	}
	return string(out), nil
}

// Encode converts a UTF-8 string to bytes in the named encoding.
// Characters that cannot be represented cause an error.
func Encode(s, to string) ([]byte, error) {
	enc, err := Lookup(to)
	if err != nil {
		return nil, err
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), []byte(s))
	return out, err
}

// NewDecodingReader wraps r so that reads yield UTF-8 decoded from the
// named encoding.
func NewDecodingReader(r io.Reader, from string) (io.Reader, error) {
	enc, err := Lookup(from)
	if err != nil {
		return nil, err
	}
	return transform.NewReader(r, enc.NewDecoder()), nil
}

// Form is a Unicode normalization form.
type Form = norm.Form

const (
	NFC  = norm.NFC
	NFD  = norm.NFD
	NFKC = norm.NFKC
	NFKD = norm.NFKD
)

// Normalize returns s in the given normalization form.
func Normalize(s string, f Form) string {
	return f.String(s)
}
