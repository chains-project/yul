package main

import (
	"bytes"
	"fmt"
	"io"
	"strings"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/encoding/ianaindex"
	"golang.org/x/text/encoding/japanese"
	"golang.org/x/text/encoding/korean"
	"golang.org/x/text/encoding/simplifiedchinese"
	"golang.org/x/text/encoding/traditionalchinese"
	"golang.org/x/text/encoding/unicode"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// encodings maps friendly names to text encodings.
var encodings = map[string]encoding.Encoding{
	"utf-8":        unicode.UTF8,
	"utf-16":       unicode.UTF16(unicode.BigEndian, unicode.UseBOM),
	"utf-16be":     unicode.UTF16(unicode.BigEndian, unicode.IgnoreBOM),
	"utf-16le":     unicode.UTF16(unicode.LittleEndian, unicode.IgnoreBOM),
	"windows-1252": charmap.Windows1252,
	"windows-1251": charmap.Windows1251,
	"iso-8859-1":   charmap.ISO8859_1,
	"iso-8859-2":   charmap.ISO8859_2,
	"iso-8859-15":  charmap.ISO8859_15,
	"koi8-r":       charmap.KOI8R,
	"shift-jis":    japanese.ShiftJIS,
	"euc-jp":       japanese.EUCJP,
	"iso-2022-jp":  japanese.ISO2022JP,
	"euc-kr":       korean.EUCKR,
	"gbk":          simplifiedchinese.GBK,
	"gb18030":      simplifiedchinese.GB18030,
	"big5":         traditionalchinese.Big5,
}

// LookupEncoding resolves a friendly name or an IANA charset alias.
func LookupEncoding(name string) (encoding.Encoding, error) {
	if enc, ok := encodings[strings.ToLower(strings.TrimSpace(name))]; ok {
		return enc, nil
	}
	enc, err := ianaindex.IANA.Encoding(name)
	if err != nil {
		return nil, fmt.Errorf("unknown encoding %q: %w", name, err)
	}
	if enc == nil {
		return nil, fmt.Errorf("encoding %q is not supported", name)
	}
	return enc, nil
}

// Convert transcodes src from the named source encoding into UTF-8.
func Convert(src []byte, from string) ([]byte, error) {
	enc, err := LookupEncoding(from)
	if err != nil {
		return nil, err
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), src)
	if err != nil {
		return nil, fmt.Errorf("decode %s: %w", from, err)
	}
	return out, nil
}

// Encode transcodes UTF-8 src into the named target encoding.
func Encode(src []byte, to string) ([]byte, error) {
	enc, err := LookupEncoding(to)
	if err != nil {
		return nil, err
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), src)
	if err != nil {
		return nil, fmt.Errorf("encode %s: %w", to, err)
	}
	return out, nil
}

// Normalize applies the requested Unicode normalization form.
func Normalize(src []byte, form string) ([]byte, error) {
	var f norm.Form
	switch strings.ToUpper(strings.TrimSpace(form)) {
	case "NFC":
		f = norm.NFC
	case "NFD":
		f = norm.NFD
	case "NFKC":
		f = norm.NFKC
	case "NFKD":
		f = norm.NFKD
	default:
		return nil, fmt.Errorf("unknown normalization form %q (want NFC, NFD, NFKC or NFKD)", form)
	}
	return f.Bytes(src), nil
}

// ConvertAndNormalize decodes from an encoding, normalizes, then re-encodes.
func ConvertAndNormalize(src []byte, from, to, form string) ([]byte, error) {
	utf8, err := Convert(src, from)
	if err != nil {
		return nil, err
	}
	utf8, err = Normalize(utf8, form)
	if err != nil {
		return nil, err
	}
	return Encode(utf8, to)
}

// Reader wraps r with a streaming decoder and optional normalization.
func Reader(r io.Reader, from, form string) (io.Reader, error) {
	utf8, err := ConvertReader(r, from)
	if err != nil {
		return nil, err
	}
	if form == "" {
		return utf8, nil
	}
	f, err := normForm(form)
	if err != nil {
		return nil, err
	}
	return transform.NewReader(utf8, f), nil
}

// ConvertReader streams a decoder from the named encoding into UTF-8.
func ConvertReader(r io.Reader, from string) (io.Reader, error) {
	enc, err := LookupEncoding(from)
	if err != nil {
		return nil, err
	}
	return transform.NewReader(r, enc.NewDecoder()), nil
}

func normForm(form string) (norm.Form, error) {
	switch strings.ToUpper(strings.TrimSpace(form)) {
	case "NFC":
		return norm.NFC, nil
	case "NFD":
		return norm.NFD, nil
	case "NFKC":
		return norm.NFKC, nil
	case "NFKD":
		return norm.NFKD, nil
	default:
		return 0, fmt.Errorf("unknown normalization form %q", form)
	}
}

// EqualFold reports whether a and b are equal under Unicode case folding and
// NFC normalization.
func EqualFold(a, b []byte) bool {
	return bytes.Equal(norm.NFC.Bytes(a), norm.NFC.Bytes(b)) ||
		strings.EqualFold(string(a), string(b))
}
