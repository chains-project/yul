// Package textconv converts text between character encodings and applies
// Unicode normalization.
//
// It builds on golang.org/x/text: decoding turns bytes in a source encoding
// into UTF-8, normalization operates on that UTF-8, and encoding turns UTF-8
// into the destination encoding.
package textconv

import (
	"fmt"
	"io"

	"golang.org/x/text/encoding"
	"golang.org/x/text/transform"
)

// Decode converts data from the named source encoding into UTF-8. Invalid
// input sequences are replaced with U+FFFD.
func Decode(data []byte, src string) ([]byte, error) {
	enc, err := Lookup(src)
	if err != nil {
		return nil, err
	}
	return decode(data, enc)
}

func decode(data []byte, enc encoding.Encoding) ([]byte, error) {
	out, _, err := transform.Bytes(enc.NewDecoder(), data)
	if err != nil {
		return nil, fmt.Errorf("textconv: decode: %w", err)
	}
	return out, nil
}

// Encode converts UTF-8 text into the named destination encoding. Runes that
// cannot be represented are replaced with the encoding's substitution, usually
// '?'.
func Encode(utf8 []byte, dst string) ([]byte, error) {
	enc, err := Lookup(dst)
	if err != nil {
		return nil, err
	}
	return encode(utf8, enc)
}

func encode(utf8 []byte, enc encoding.Encoding) ([]byte, error) {
	out, _, err := transform.Bytes(encoding.ReplaceUnsupported(enc.NewEncoder()), utf8)
	if err != nil {
		return nil, fmt.Errorf("textconv: encode: %w", err)
	}
	return out, nil
}

// Convert decodes data from the from encoding, normalizes it to n (when n is
// not None), and encodes the result as to.
func Convert(data []byte, from, to string, n Normalization) ([]byte, error) {
	utf8, err := Decode(data, from)
	if err != nil {
		return nil, err
	}
	if n != None {
		utf8 = []byte(Normalize(string(utf8), n))
	}
	return Encode(utf8, to)
}

// NewReader returns a reader that decodes the underlying stream from src into
// UTF-8.
func NewReader(r io.Reader, src string) (io.Reader, error) {
	enc, err := Lookup(src)
	if err != nil {
		return nil, err
	}
	return transform.NewReader(r, enc.NewDecoder()), nil
}

// NewWriter returns a writer that normalizes UTF-8 input to n and encodes it
// as dst before writing to w. Callers must call Close to flush trailing bytes.
func NewWriter(w io.Writer, dst string, n Normalization) (io.WriteCloser, error) {
	enc, err := Lookup(dst)
	if err != nil {
		return nil, err
	}
	if n == None {
		return transform.NewWriter(w, encoding.ReplaceUnsupported(enc.NewEncoder())), nil
	}
	return transform.NewWriter(w, transform.Chain(n.form(), encoding.ReplaceUnsupported(enc.NewEncoder()))), nil
}
