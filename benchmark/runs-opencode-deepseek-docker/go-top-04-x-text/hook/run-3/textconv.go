// Package main implements textconv, a command-line tool and small library for
// converting text between character encodings and applying Unicode
// normalization forms.
package main

import (
	"fmt"
	"strings"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// LookupEncoding resolves an encoding by its IANA/WHATWG name, for example
// "utf-8", "utf-16le", "windows-1252", "shift_jis" or "iso-8859-1". An empty
// name defaults to UTF-8.
func LookupEncoding(name string) (encoding.Encoding, error) {
	if name == "" {
		name = "utf-8"
	}
	enc, err := htmlindex.Get(name)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q", name)
	}
	return enc, nil
}

// Decode converts bytes in the given encoding to a UTF-8 string. A nil
// encoding is treated as UTF-8.
func Decode(data []byte, enc encoding.Encoding) (string, error) {
	if enc == nil {
		return string(data), nil
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), data)
	if err != nil {
		return "", fmt.Errorf("decoding to UTF-8: %w", err)
	}
	return string(out), nil
}

// Encode converts a UTF-8 string to bytes in the given encoding. A nil
// encoding is treated as UTF-8.
func Encode(s string, enc encoding.Encoding) ([]byte, error) {
	if enc == nil {
		return []byte(s), nil
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), []byte(s))
	if err != nil {
		return nil, fmt.Errorf("encoding from UTF-8: %w", err)
	}
	return out, nil
}

// Normalize applies the given Unicode normalization form to s. A nil form
// leaves s unchanged.
func Normalize(s string, form *norm.Form) string {
	if form == nil {
		return s
	}
	return form.String(s)
}

// Convert decodes data from the from encoding, applies the optional
// normalization form, and encodes the result using the to encoding. Nil
// encodings are treated as UTF-8.
func Convert(data []byte, from, to encoding.Encoding, form *norm.Form) ([]byte, error) {
	s, err := Decode(data, from)
	if err != nil {
		return nil, err
	}
	s = Normalize(s, form)
	return Encode(s, to)
}

// ParseForm maps a normalization form name to a norm.Form. It accepts the
// case-insensitive names "nfc", "nfd", "nfkc" and "nfkd"; "none" and "" return
// a nil form.
func ParseForm(name string) (*norm.Form, error) {
	switch strings.ToLower(strings.TrimSpace(name)) {
	case "", "none":
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
		return nil, fmt.Errorf("unknown normalization form %q (want none, nfc, nfd, nfkc or nfkd)", name)
	}
}
