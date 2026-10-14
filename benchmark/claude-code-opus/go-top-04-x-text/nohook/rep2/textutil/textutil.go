// Package textutil provides helpers for converting between character
// encodings and normalizing Unicode text.
package textutil

import (
	"fmt"
	"strings"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// lookup resolves an encoding by its WHATWG/IANA name (e.g. "shift_jis", "windows-1252").
func lookup(name string) (encoding.Encoding, error) {
	enc, err := htmlindex.Get(name)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q: %w", name, err)
	}
	return enc, nil
}

// ToUTF8 decodes src from the named encoding into a UTF-8 string.
func ToUTF8(src []byte, from string) (string, error) {
	enc, err := lookup(from)
	if err != nil {
		return "", err
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), src)
	if err != nil {
		return "", fmt.Errorf("decode from %s: %w", from, err)
	}
	return string(out), nil
}

// FromUTF8 encodes a UTF-8 string into the named encoding.
func FromUTF8(s string, to string) ([]byte, error) {
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

// Normalize returns s in the given Unicode normalization form.
func Normalize(s string, form norm.Form) string {
	return form.String(s)
}

// ParseForm maps "NFC", "NFD", "NFKC" or "NFKD" (case-insensitive) to a norm.Form.
func ParseForm(name string) (norm.Form, error) {
	switch strings.ToUpper(name) {
	case "NFC":
		return norm.NFC, nil
	case "NFD":
		return norm.NFD, nil
	case "NFKC":
		return norm.NFKC, nil
	case "NFKD":
		return norm.NFKD, nil
	}
	return 0, fmt.Errorf("unknown normalization form %q", name)
}
