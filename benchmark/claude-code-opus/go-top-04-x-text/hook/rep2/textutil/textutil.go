// Package textutil provides helpers for character-encoding conversion and
// Unicode normalization, built on golang.org/x/text.
package textutil

import (
	"fmt"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/unicode/norm"
)

// lookup resolves an encoding by its WHATWG/IANA name (e.g. "shift_jis",
// "windows-1252", "iso-8859-1").
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
	out, err := enc.NewDecoder().Bytes(b)
	if err != nil {
		return "", fmt.Errorf("decode from %s: %w", from, err)
	}
	return string(out), nil
}

// EncodeFromUTF8 converts a UTF-8 string to bytes in the named encoding.
// It returns an error if s contains characters the target cannot represent.
func EncodeFromUTF8(s, to string) ([]byte, error) {
	enc, err := lookup(to)
	if err != nil {
		return nil, err
	}
	out, err := enc.NewEncoder().Bytes([]byte(s))
	if err != nil {
		return nil, fmt.Errorf("encode to %s: %w", to, err)
	}
	return out, nil
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

// EqualNormalized reports whether a and b are canonically equivalent
// (equal after NFC normalization).
func EqualNormalized(a, b string) bool {
	return norm.NFC.String(a) == norm.NFC.String(b)
}
