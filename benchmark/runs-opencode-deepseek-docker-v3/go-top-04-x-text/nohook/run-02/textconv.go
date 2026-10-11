// Package textconv provides helpers for converting between text encodings and
// applying Unicode normalization forms.
package textconv

import (
	"fmt"
	"sort"
	"strings"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/encoding/japanese"
	"golang.org/x/text/encoding/korean"
	"golang.org/x/text/encoding/simplifiedchinese"
	"golang.org/x/text/encoding/traditionalchinese"
	"golang.org/x/text/encoding/unicode"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// encodings maps stable, case-insensitive names to their x/text encoding.
var encodings = map[string]encoding.Encoding{
	"utf-8":        unicode.UTF8,
	"utf-16":       unicode.UTF16(unicode.LittleEndian, unicode.UseBOM),
	"utf-16le":     unicode.UTF16(unicode.LittleEndian, unicode.IgnoreBOM),
	"utf-16be":     unicode.UTF16(unicode.BigEndian, unicode.IgnoreBOM),
	"windows-1252": charmap.Windows1252,
	"iso-8859-1":   charmap.ISO8859_1,
	"iso-8859-15":  charmap.ISO8859_15,
	"koi8-r":       charmap.KOI8R,
	"shift_jis":    japanese.ShiftJIS,
	"euc-jp":       japanese.EUCJP,
	"euc-kr":       korean.EUCKR,
	"gbk":          simplifiedchinese.GBK,
	"gb18030":      simplifiedchinese.GB18030,
	"big5":         traditionalchinese.Big5,
}

// Encodings returns the sorted list of supported encoding names.
func Encodings() []string {
	names := make([]string, 0, len(encodings))
	for name := range encodings {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// Normalization forms accepted by Normalize.
const (
	NFC  = "NFC"
	NFD  = "NFD"
	NFKC = "NFKC"
	NFKD = "NFKD"
)

var forms = map[string]norm.Form{
	NFC:  norm.NFC,
	NFD:  norm.NFD,
	NFKC: norm.NFKC,
	NFKD: norm.NFKD,
}

// Decode converts data from the named encoding into a UTF-8 string.
func Decode(data []byte, encodingName string) (string, error) {
	enc, err := lookup(encodingName)
	if err != nil {
		return "", err
	}
	out, _, err := transform.String(enc.NewDecoder(), string(data))
	if err != nil {
		return "", fmt.Errorf("decode %s: %w", encodingName, err)
	}
	return out, nil
}

// Encode converts a UTF-8 string into data in the named encoding.
func Encode(s, encodingName string) ([]byte, error) {
	enc, err := lookup(encodingName)
	if err != nil {
		return nil, err
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), []byte(s))
	if err != nil {
		return nil, fmt.Errorf("encode %s: %w", encodingName, err)
	}
	return out, nil
}

// Convert transcodes data from one encoding to another.
func Convert(data []byte, from, to string) ([]byte, error) {
	s, err := Decode(data, from)
	if err != nil {
		return nil, err
	}
	return Encode(s, to)
}

// Normalize applies the requested Unicode normalization form to s. The form is
// case-insensitive and defaults to NFC when empty.
func Normalize(s, form string) (string, error) {
	f, ok := forms[strings.ToUpper(form)]
	if !ok {
		if form == "" {
			f = norm.NFC
		} else {
			return "", fmt.Errorf("unsupported normalization form %q", form)
		}
	}
	return f.String(s), nil
}

func lookup(name string) (encoding.Encoding, error) {
	enc, ok := encodings[strings.ToLower(strings.TrimSpace(name))]
	if !ok {
		return nil, fmt.Errorf("unsupported encoding %q", name)
	}
	return enc, nil
}
