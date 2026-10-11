package main

import (
	"flag"
	"fmt"
	"io"
	"os"

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

var encodings = map[string]encoding.Encoding{
	"utf-8":        nil,
	"utf-16be":     unicode.UTF16(unicode.BigEndian, unicode.IgnoreBOM),
	"utf-16le":     unicode.UTF16(unicode.LittleEndian, unicode.IgnoreBOM),
	"windows-1252": charmap.Windows1252,
	"latin-1":      charmap.ISO8859_1,
	"iso-8859-15":  charmap.ISO8859_15,
	"shift-jis":    japanese.ShiftJIS,
	"euc-jp":       japanese.EUCJP,
	"euc-kr":       korean.EUCKR,
	"gbk":          simplifiedchinese.GBK,
	"gb18030":      simplifiedchinese.GB18030,
	"big5":         traditionalchinese.Big5,
}

var normalizers = map[string]norm.Form{
	"nfc":  norm.NFC,
	"nfd":  norm.NFD,
	"nfkc": norm.NFKC,
	"nfkd": norm.NFKD,
}

func main() {
	srcName := flag.String("from", "utf-8", "source encoding")
	normName := flag.String("norm", "nfc", "unicode normalization form (nfc, nfd, nfkc, nfkd)")
	flag.Parse()

	src, ok := encodings[*srcName]
	if !ok {
		fmt.Fprintf(os.Stderr, "unknown source encoding %q\n", *srcName)
		os.Exit(2)
	}

	form, ok := normalizers[*normName]
	if !ok {
		fmt.Fprintf(os.Stderr, "unknown normalization form %q\n", *normName)
		os.Exit(2)
	}

	if err := run(os.Stdin, os.Stdout, src, form); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

func run(r io.Reader, w io.Writer, src encoding.Encoding, form norm.Form) error {
	if src != nil {
		r = transform.NewReader(r, src.NewDecoder())
	}
	if _, err := io.Copy(w, transform.NewReader(r, form)); err != nil {
		return err
	}
	return nil
}
