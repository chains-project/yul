package textcodec

import (
	"fmt"
	"strings"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/htmlindex"
	"golang.org/x/text/transform"
)

// LookupEncoding resolves a character encoding by its name or alias. It accepts
// the names used by the WHATWG Encoding Standard (for example "utf-8",
// "windows-1252", "shift_jis" or "gbk"), case-insensitively. An empty name, or
// "utf-8", resolves to UTF-8.
func LookupEncoding(name string) (encoding.Encoding, error) {
	if name == "" || strings.EqualFold(name, "utf-8") || strings.EqualFold(name, "utf8") {
		return encoding.Nop, nil
	}

	enc, err := htmlindex.Get(name)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q: %w", name, err)
	}
	return enc, nil
}

// Decode converts src from the given encoding to UTF-8. A nil encoding, or
// encoding.Nop, is treated as UTF-8 and returned unchanged.
func Decode(src []byte, enc encoding.Encoding) ([]byte, error) {
	out, _, err := transform.Bytes(decoder(enc), src)
	if err != nil {
		return nil, fmt.Errorf("decode: %w", err)
	}
	return out, nil
}

// Encode converts src from UTF-8 to the given encoding. A nil encoding, or
// encoding.Nop, is treated as UTF-8 and returned unchanged.
func Encode(src []byte, enc encoding.Encoding) ([]byte, error) {
	out, _, err := transform.Bytes(encoder(enc), src)
	if err != nil {
		return nil, fmt.Errorf("encode: %w", err)
	}
	return out, nil
}

// Convert transcodes src from one encoding to another, routing through UTF-8.
func Convert(src []byte, from, to encoding.Encoding) ([]byte, error) {
	utf8, err := Decode(src, from)
	if err != nil {
		return nil, err
	}
	return Encode(utf8, to)
}

func decoder(enc encoding.Encoding) transform.Transformer {
	if enc == nil || enc == encoding.Nop {
		return transform.Nop
	}
	return enc.NewDecoder()
}

func encoder(enc encoding.Encoding) transform.Transformer {
	if enc == nil || enc == encoding.Nop {
		return transform.Nop
	}
	return enc.NewEncoder()
}
