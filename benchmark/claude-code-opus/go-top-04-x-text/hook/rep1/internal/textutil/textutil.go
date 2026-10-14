// Package textutil provides helpers for character encoding conversion and
// Unicode normalization.
package textutil

import (
	"fmt"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// lookup resolves an encoding by its WHATWG/IANA name (e.g. "utf-8",
// "windows-1252", "shift_jis", "iso-8859-1").
func lookup(name string) (encoding.Encoding, error) {
	enc, err := htmlindex.Get(name)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q: %w", name, err)
	}
	return enc, nil
}

// DecodeToUTF8 converts bytes in the named encoding to a UTF-8 string.
func DecodeToUTF8(b []byte, from string) (string, error) {
	enc, err := lookup(from)
	if err != nil {
		return "", err
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), b)
	if err != nil {
		return "", fmt.Errorf("decode from %s: %w", from, err)
	}
	return string(out), nil
}

// EncodeFromUTF8 converts a UTF-8 string to bytes in the named encoding.
// Characters not representable in the target encoding cause an error.
func EncodeFromUTF8(s, to string) ([]byte, error) {
	enc, err := lookup(to)
	if err != nil {
		return nil, err
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), []byte(s))
	if err != nil {
		return nil, fmt.Errorf("encode to %s: %w", to, err)
	}
	return out, nil
}

// Convert re-encodes b from one named encoding to another.
func Convert(b []byte, from, to string) ([]byte, error) {
	s, err := DecodeToUTF8(b, from)
	if err != nil {
		return nil, err
	}
	return EncodeFromUTF8(s, to)
}

// Form is a Unicode normalization form.
type Form = norm.Form

const (
	NFC  = norm.NFC
	NFD  = norm.NFD
	NFKC = norm.NFKC
	NFKD = norm.NFKD
)

// Normalize returns s normalized to the given form.
func Normalize(s string, f Form) string {
	return f.String(s)
}
