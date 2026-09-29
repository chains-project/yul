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
)

// encodings maps canonical, lower-case encoding names to their implementations.
// Names use hyphens; Lookup normalizes other spellings before consulting it.
var encodings = map[string]encoding.Encoding{
	"utf-8":        unicode.UTF8,
	"utf-16":       unicode.UTF16(unicode.BigEndian, unicode.UseBOM),
	"utf-16be":     unicode.UTF16(unicode.BigEndian, unicode.IgnoreBOM),
	"utf-16le":     unicode.UTF16(unicode.LittleEndian, unicode.IgnoreBOM),
	"iso-8859-1":   charmap.ISO8859_1,
	"iso-8859-15":  charmap.ISO8859_15,
	"windows-1252": charmap.Windows1252,
	"koi8-r":       charmap.KOI8R,
	"macintosh":    charmap.Macintosh,
	"cp437":        charmap.CodePage437,
	"shift-jis":    japanese.ShiftJIS,
	"euc-jp":       japanese.EUCJP,
	"iso-2022-jp":  japanese.ISO2022JP,
	"euc-kr":       korean.EUCKR,
	"gbk":          simplifiedchinese.GBK,
	"gb18030":      simplifiedchinese.GB18030,
	"hz-gb2312":    simplifiedchinese.HZGB2312,
	"big5":         traditionalchinese.Big5,
}

// encodingAliases resolves common alternative spellings to canonical names.
// Keys are compared after normalizeName is applied.
var encodingAliases = map[string]string{
	"utf8":        "utf-8",
	"utf16":       "utf-16",
	"utf16be":     "utf-16be",
	"utf16le":     "utf-16le",
	"unicode":     "utf-16le",
	"latin1":      "iso-8859-1",
	"latin-1":     "iso-8859-1",
	"iso8859-1":   "iso-8859-1",
	"latin9":      "iso-8859-15",
	"cp1252":      "windows-1252",
	"windows1252": "windows-1252",
	"cp932":       "shift-jis",
	"sjis":        "shift-jis",
	"shiftjis":    "shift-jis",
	"cp949":       "euc-kr",
	"cp936":       "gbk",
	"cp950":       "big5",
	"koi8r":       "koi8-r",
	"mac":         "macintosh",
	"mac-roman":   "macintosh",
	"ibm437":      "cp437",
	"iso2022-jp":  "iso-2022-jp",
	"hzgb2312":    "hz-gb2312",
}

// Lookup returns the encoding registered under name. Matching is
// case-insensitive and ignores underscores, so "UTF_8", "utf-8" and "utf8" all
// resolve to the same encoding.
func Lookup(name string) (encoding.Encoding, error) {
	key := normalizeName(name)
	if enc, ok := encodings[key]; ok {
		return enc, nil
	}
	if canonical, ok := encodingAliases[key]; ok {
		return encodings[canonical], nil
	}
	return nil, fmt.Errorf("textconv: unknown encoding %q", name)
}

// Names returns the sorted list of canonical encoding names.
func Names() []string {
	names := make([]string, 0, len(encodings))
	for name := range encodings {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

func normalizeName(name string) string {
	name = strings.ToLower(strings.TrimSpace(name))
	return strings.ReplaceAll(name, "_", "-")
}
