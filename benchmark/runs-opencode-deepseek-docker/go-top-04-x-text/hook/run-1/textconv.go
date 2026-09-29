// Package textconv provides helpers for converting text between character
// encodings and for applying Unicode normalization forms.
//
// Conversions are performed through UTF-8: input bytes are decoded from the
// source encoding, normalized while in UTF-8, and then encoded into the target
// encoding. This mirrors the pipeline used by the textconv command.
package textconv

import (
	"fmt"
	"io"
	"sort"
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

// Form identifies a Unicode normalization form. The zero value, None, leaves
// text unchanged.
type Form int

const (
	None Form = iota
	NFC
	NFD
	NFKC
	NFKD
)

// String returns the standard name of the form.
func (f Form) String() string {
	switch f {
	case NFC:
		return "NFC"
	case NFD:
		return "NFD"
	case NFKC:
		return "NFKC"
	case NFKD:
		return "NFKD"
	default:
		return "None"
	}
}

// ParseForm converts a case-insensitive normalization form name ("NFC", "nfkd",
// "none", ...) into a Form.
func ParseForm(name string) (Form, bool) {
	switch strings.ToUpper(strings.TrimSpace(name)) {
	case "", "NONE":
		return None, true
	case "NFC":
		return NFC, true
	case "NFD":
		return NFD, true
	case "NFKC":
		return NFKC, true
	case "NFKD":
		return NFKD, true
	default:
		return None, false
	}
}

// Normalize returns s normalized using the given form. None is a no-op.
func Normalize(s string, form Form) string {
	switch form {
	case NFC:
		return norm.NFC.String(s)
	case NFD:
		return norm.NFD.String(s)
	case NFKC:
		return norm.NFKC.String(s)
	case NFKD:
		return norm.NFKD.String(s)
	default:
		return s
	}
}

// IsNormalized reports whether s is already in the given normalization form.
// None is always reported as normalized.
func IsNormalized(s string, form Form) bool {
	switch form {
	case NFC:
		return norm.NFC.IsNormalString(s)
	case NFD:
		return norm.NFD.IsNormalString(s)
	case NFKC:
		return norm.NFKC.IsNormalString(s)
	case NFKD:
		return norm.NFKD.IsNormalString(s)
	default:
		return true
	}
}

// ascii is the US-ASCII encoding. The x/text package keeps its only ASCII
// codec in ianaindex, so it is resolved there rather than in charmap.
var ascii = func() encoding.Encoding {
	enc, err := ianaindex.MIB.Encoding("US-ASCII")
	if err != nil {
		panic("textconv: US-ASCII encoding unavailable: " + err.Error())
	}
	return enc
}()

var encodings = map[string]encoding.Encoding{
	"utf-8":        unicode.UTF8,
	"utf-16":       unicode.UTF16(unicode.BigEndian, unicode.UseBOM),
	"utf-16be":     unicode.UTF16(unicode.BigEndian, unicode.IgnoreBOM),
	"utf-16le":     unicode.UTF16(unicode.LittleEndian, unicode.IgnoreBOM),
	"us-ascii":     ascii,
	"iso-8859-1":   charmap.ISO8859_1,
	"iso-8859-2":   charmap.ISO8859_2,
	"iso-8859-15":  charmap.ISO8859_15,
	"windows-1252": charmap.Windows1252,
	"koi8-r":       charmap.KOI8R,
	"shift_jis":    japanese.ShiftJIS,
	"euc-jp":       japanese.EUCJP,
	"iso-2022-jp":  japanese.ISO2022JP,
	"euc-kr":       korean.EUCKR,
	"gbk":          simplifiedchinese.GBK,
	"gb18030":      simplifiedchinese.GB18030,
	"hz-gb-2312":   simplifiedchinese.HZGB2312,
	"big5":         traditionalchinese.Big5,
}

var aliases = map[string]string{
	"utf8":      "utf-8",
	"utf16":     "utf-16",
	"utf16be":   "utf-16be",
	"utf16le":   "utf-16le",
	"ascii":     "us-ascii",
	"latin1":    "iso-8859-1",
	"latin-1":   "iso-8859-1",
	"cp1252":    "windows-1252",
	"sjis":      "shift_jis",
	"shift-jis": "shift_jis",
	"cp932":     "shift_jis",
	"eucjp":     "euc-jp",
	"euckr":     "euc-kr",
	"cp949":     "euc-kr",
	"gb2312":    "gbk",
	"chinese":   "gbk",
	"big-5":     "big5",
}

// Lookup resolves a case-insensitive encoding name or alias to an encoding.
func Lookup(name string) (encoding.Encoding, bool) {
	key := strings.ToLower(strings.TrimSpace(name))
	if canonical, ok := aliases[key]; ok {
		key = canonical
	}
	enc, ok := encodings[key]
	return enc, ok
}

// Encodings returns the sorted list of canonical encoding names understood by
// Lookup.
func Encodings() []string {
	names := make([]string, 0, len(encodings))
	for name := range encodings {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// Decode interprets data as text in the from encoding and returns it as UTF-8.
// A nil encoding is treated as UTF-8.
func Decode(data []byte, from encoding.Encoding) (string, error) {
	if from == nil || from == encoding.Nop {
		return string(data), nil
	}
	out, _, err := transform.Bytes(from.NewDecoder(), data)
	if err != nil {
		return "", fmt.Errorf("decode: %w", err)
	}
	return string(out), nil
}

// Encode converts the UTF-8 string s into the to encoding. A nil encoding is
// treated as UTF-8.
func Encode(s string, to encoding.Encoding) ([]byte, error) {
	if to == nil || to == encoding.Nop {
		return []byte(s), nil
	}
	out, _, err := transform.Bytes(to.NewEncoder(), []byte(s))
	if err != nil {
		return nil, fmt.Errorf("encode: %w", err)
	}
	return out, nil
}

// Convert decodes data from the from encoding, normalizes the resulting text
// using form, and encodes it into the to encoding. The result is always valid
// for the target encoding.
func Convert(data []byte, from, to encoding.Encoding, form Form) ([]byte, error) {
	decoded, err := Decode(data, from)
	if err != nil {
		return nil, err
	}
	return Encode(Normalize(decoded, form), to)
}

// ConvertString is like Convert but takes and returns strings.
func ConvertString(s string, from, to encoding.Encoding, form Form) (string, error) {
	out, err := Convert([]byte(s), from, to, form)
	if err != nil {
		return "", err
	}
	return string(out), nil
}

// NewReader returns a reader that decodes r from the from encoding into UTF-8
// and applies the given normalization form.
func NewReader(r io.Reader, from encoding.Encoding, form Form) io.Reader {
	var t transform.Transformer
	if from != nil && from != encoding.Nop {
		t = from.NewDecoder()
	}
	if form != None {
		t = transform.Chain(t, form.transformer())
	}
	if t == nil {
		return r
	}
	return transform.NewReader(r, t)
}

// NewWriter returns a writer that encodes UTF-8 written to it into the to
// encoding. The caller is responsible for closing the returned WriteCloser.
func NewWriter(w io.Writer, to encoding.Encoding) io.WriteCloser {
	if to == nil || to == encoding.Nop {
		return nopWriteCloser{w}
	}
	return transform.NewWriter(w, to.NewEncoder())
}

// transformer returns the streaming transformer for the form. None is handled
// by callers and must not reach this method.
func (f Form) transformer() transform.Transformer {
	switch f {
	case NFC:
		return norm.NFC
	case NFD:
		return norm.NFD
	case NFKC:
		return norm.NFKC
	case NFKD:
		return norm.NFKD
	default:
		return nil
	}
}

type nopWriteCloser struct {
	io.Writer
}

func (nopWriteCloser) Close() error { return nil }
