package textconv

import (
	"fmt"
	"io"
	"strings"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/encoding/japanese"
	"golang.org/x/text/encoding/simplifiedchinese"
	"golang.org/x/text/encoding/traditionalchinese"
	"golang.org/x/text/encoding/unicode"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

var registry = map[string]encoding.Encoding{
	"utf-8":        unicode.UTF8,
	"utf-16":       unicode.UTF16(unicode.BigEndian, unicode.UseBOM),
	"utf-16le":     unicode.UTF16(unicode.LittleEndian, unicode.IgnoreBOM),
	"utf-16be":     unicode.UTF16(unicode.BigEndian, unicode.IgnoreBOM),
	"iso-8859-1":   charmap.ISO8859_1,
	"iso-8859-2":   charmap.ISO8859_2,
	"iso-8859-15":  charmap.ISO8859_15,
	"windows-1250": charmap.Windows1250,
	"windows-1251": charmap.Windows1251,
	"windows-1252": charmap.Windows1252,
	"windows-1256": charmap.Windows1256,
	"koi8-r":       charmap.KOI8R,
	"shift_jis":    japanese.ShiftJIS,
	"euc-jp":       japanese.EUCJP,
	"iso-2022-jp":  japanese.ISO2022JP,
	"gbk":          simplifiedchinese.GBK,
	"gb18030":      simplifiedchinese.GB18030,
	"hz-gb2312":    simplifiedchinese.HZGB2312,
	"big5":         traditionalchinese.Big5,
}

func Lookup(name string) (encoding.Encoding, bool) {
	enc, ok := registry[strings.ToLower(strings.TrimSpace(name))]
	return enc, ok
}

func Decode(data []byte, enc encoding.Encoding) ([]byte, error) {
	if enc == nil {
		return nil, fmt.Errorf("textconv: decode: nil encoding")
	}
	out, _, err := transform.Bytes(enc.NewDecoder(), data)
	if err != nil {
		return nil, fmt.Errorf("textconv: decode: %w", err)
	}
	return out, nil
}

func Encode(s string, enc encoding.Encoding) ([]byte, error) {
	if enc == nil {
		return nil, fmt.Errorf("textconv: encode: nil encoding")
	}
	out, _, err := transform.Bytes(enc.NewEncoder(), []byte(s))
	if err != nil {
		return nil, fmt.Errorf("textconv: encode: %w", err)
	}
	return out, nil
}

func DecodeString(data []byte, enc encoding.Encoding) (string, error) {
	out, err := Decode(data, enc)
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func Convert(data []byte, enc encoding.Encoding, form norm.Form) ([]byte, error) {
	out, err := Decode(data, enc)
	if err != nil {
		return nil, err
	}
	return form.Bytes(out), nil
}

func Normalize(s string, form norm.Form) string {
	return form.String(s)
}

func NormalizeReader(r io.Reader, form norm.Form) io.Reader {
	return transform.NewReader(r, form)
}

func IsNormalized(s string, form norm.Form) bool {
	return form.IsNormalString(s)
}

func ToNFC(s string) string { return norm.NFC.String(s) }

func ToNFD(s string) string { return norm.NFD.String(s) }

func ToNFKC(s string) string { return norm.NFKC.String(s) }

func ToNFKD(s string) string { return norm.NFKD.String(s) }
