// Package textconv provides text encoding conversion and Unicode
// normalization helpers.
package textconv

import (
	"fmt"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// Lookup resolves an encoding by its WHATWG/IANA name, such as "utf-8",
// "windows-1252", "iso-8859-1" or "shift_jis".
func Lookup(name string) (encoding.Encoding, error) {
	e, err := htmlindex.Get(name)
	if err != nil {
		return nil, fmt.Errorf("textconv: unknown encoding %q: %w", name, err)
	}
	return e, nil
}

// Decode converts b, encoded with from, into a UTF-8 string.
func Decode(b []byte, from encoding.Encoding) (string, error) {
	out, _, err := transform.Bytes(from.NewDecoder(), b)
	if err != nil {
		return "", fmt.Errorf("textconv: decode: %w", err)
	}
	return string(out), nil
}

// Encode converts the UTF-8 string s into bytes encoded with to.
func Encode(s string, to encoding.Encoding) ([]byte, error) {
	out, _, err := transform.Bytes(to.NewEncoder(), []byte(s))
	if err != nil {
		return nil, fmt.Errorf("textconv: encode: %w", err)
	}
	return out, nil
}

// Transcode converts b from the from encoding directly into the to encoding.
func Transcode(b []byte, from, to encoding.Encoding) ([]byte, error) {
	t := transform.Chain(from.NewDecoder(), to.NewEncoder())
	out, _, err := transform.Bytes(t, b)
	if err != nil {
		return nil, fmt.Errorf("textconv: transcode: %w", err)
	}
	return out, nil
}

// Convert decodes b using from and applies the given Unicode normalization
// form to the resulting UTF-8 text.
func Convert(b []byte, from encoding.Encoding, form norm.Form) (string, error) {
	s, err := Decode(b, from)
	if err != nil {
		return "", err
	}
	return form.String(s), nil
}

// Normalize applies the given Unicode normalization form to s.
func Normalize(s string, form norm.Form) string {
	return form.String(s)
}

// NFC returns s normalized to Unicode Normalization Form C (canonical
// composition).
func NFC(s string) string { return norm.NFC.String(s) }

// NFD returns s normalized to Unicode Normalization Form D (canonical
// decomposition).
func NFD(s string) string { return norm.NFD.String(s) }

// NFKC returns s normalized to Unicode Normalization Form KC (compatibility
// composition).
func NFKC(s string) string { return norm.NFKC.String(s) }

// NFKD returns s normalized to Unicode Normalization Form KD (compatibility
// decomposition).
func NFKD(s string) string { return norm.NFKD.String(s) }
