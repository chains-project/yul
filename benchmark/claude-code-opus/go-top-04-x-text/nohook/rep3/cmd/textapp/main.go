// Command textapp converts text between encodings and normalizes it.
//
//	textapp -from shift_jis -to utf-8 -norm NFC < in.txt > out.txt
package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"strings"

	"example.com/textapp/internal/textconv"
)

func main() {
	from := flag.String("from", "utf-8", "input encoding")
	to := flag.String("to", "utf-8", "output encoding")
	form := flag.String("norm", "", "normalization form: NFC, NFD, NFKC, NFKD (default none)")
	flag.Parse()

	if err := run(os.Stdin, os.Stdout, *from, *to, *form); err != nil {
		fmt.Fprintln(os.Stderr, "textapp:", err)
		os.Exit(1)
	}
}

func run(in io.Reader, out io.Writer, from, to, form string) error {
	r, err := textconv.NewDecodingReader(in, from)
	if err != nil {
		return err
	}
	b, err := io.ReadAll(r)
	if err != nil {
		return err
	}
	s := string(b)

	if form != "" {
		f, ok := map[string]textconv.Form{
			"NFC": textconv.NFC, "NFD": textconv.NFD,
			"NFKC": textconv.NFKC, "NFKD": textconv.NFKD,
		}[strings.ToUpper(form)]
		if !ok {
			return fmt.Errorf("unknown normalization form %q", form)
		}
		s = textconv.Normalize(s, f)
	}

	enc, err := textconv.Encode(s, to)
	if err != nil {
		return err
	}
	_, err = out.Write(enc)
	return err
}
