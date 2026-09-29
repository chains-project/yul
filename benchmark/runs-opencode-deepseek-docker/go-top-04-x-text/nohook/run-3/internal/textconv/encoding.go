// Package textconv provides helpers for converting between text encodings and
// for normalizing Unicode strings.
package textconv

import (
	"fmt"
	"io"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/ianaindex"
	"golang.org/x/text/transform"
)

// Encoding returns the encoding registered under the given IANA charset name.
// Names are matched case-insensitively, for example "utf-8", "iso-8859-1",
// "shift_jis" or "windows-1252".
func Encoding(name string) (encoding.Encoding, error) {
	enc, err := ianaindex.IANA.Encoding(name)
	if err != nil {
		return nil, fmt.Errorf("textconv: unknown charset %q: %w", name, err)
	}
	if enc == nil {
		return nil, fmt.Errorf("textconv: unknown charset %q", name)
	}
	return enc, nil
}

// Convert re-encodes src from the source charset to the target charset. It
// returns an error if either charset is unknown or if src is not valid in the
// source charset.
func Convert(src []byte, source, target string) ([]byte, error) {
	srcEnc, err := Encoding(source)
	if err != nil {
		return nil, err
	}
	dstEnc, err := Encoding(target)
	if err != nil {
		return nil, err
	}
	out, _, err := transform.Bytes(transform.Chain(srcEnc.NewDecoder(), dstEnc.NewEncoder()), src)
	if err != nil {
		return nil, fmt.Errorf("textconv: convert %s to %s: %w", source, target, err)
	}
	return out, nil
}

// Reader wraps r so that bytes are read as the source charset and returned as
// UTF-8.
func Reader(r io.Reader, source string) (io.Reader, error) {
	srcEnc, err := Encoding(source)
	if err != nil {
		return nil, err
	}
	return transform.NewReader(r, srcEnc.NewDecoder()), nil
}

// Writer wraps w so that UTF-8 bytes written to it are encoded in the target
// charset.
func Writer(w io.Writer, target string) (io.Writer, error) {
	dstEnc, err := Encoding(target)
	if err != nil {
		return nil, err
	}
	return transform.NewWriter(w, dstEnc.NewEncoder()), nil
}
