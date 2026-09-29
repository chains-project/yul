// Package textconv provides helpers for converting text between character
// encodings and applying Unicode normalization forms.
package textconv

import (
	"fmt"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/ianaindex"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// lookup resolves an encoding by its IANA name (for example "windows-1252",
// "shift_jis" or "GBK"). A nil encoding is returned for UTF-8, which is the
// assumed internal representation and therefore needs no conversion.
func lookup(name string) (encoding.Encoding, error) {
	enc, err := ianaindex.IANA.Encoding(name)
	if err != nil {
		return nil, fmt.Errorf("textconv: unknown encoding %q: %w", name, err)
	}
	return enc, nil
}

// Decode converts src from the named character encoding to UTF-8.
func Decode(name string, src []byte) ([]byte, error) {
	enc, err := lookup(name)
	if err != nil {
		return nil, err
	}
	if enc == nil {
		return append([]byte(nil), src...), nil
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), src)
	if err != nil {
		return nil, fmt.Errorf("textconv: decode %q: %w", name, err)
	}
	return out, nil
}

// Encode converts UTF-8 src to the named character encoding.
func Encode(name string, src []byte) ([]byte, error) {
	enc, err := lookup(name)
	if err != nil {
		return nil, err
	}
	if enc == nil {
		return append([]byte(nil), src...), nil
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), src)
	if err != nil {
		return nil, fmt.Errorf("textconv: encode %q: %w", name, err)
	}
	return out, nil
}

// Normalize returns s in the requested Unicode normalization form.
func Normalize(form norm.Form, s string) string {
	return form.String(s)
}

// IsNormal reports whether s is already in the requested normalization form.
func IsNormal(form norm.Form, s string) bool {
	return form.IsNormalString(s)
}
