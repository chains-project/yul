package textutil

import (
	"bytes"
	"strings"
	"testing"
)

func TestDecodeEncodeRoundTrip(t *testing.T) {
	latin1 := []byte{'c', 'a', 'f', 0xE9} // "café" in windows-1252
	s, err := Decode(latin1, "windows-1252")
	if err != nil {
		t.Fatal(err)
	}
	if s != "café" {
		t.Fatalf("Decode = %q, want %q", s, "café")
	}
	b, err := Encode(s, "windows-1252")
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(b, latin1) {
		t.Fatalf("Encode = %x, want %x", b, latin1)
	}
}

func TestEncodeUnrepresentable(t *testing.T) {
	if _, err := Encode("日本", "windows-1252"); err == nil {
		t.Fatal("expected error for unrepresentable characters")
	}
}

func TestNormalize(t *testing.T) {
	decomposed := "café"
	if got := Normalize(decomposed, NFC); got != "café" {
		t.Errorf("NFC = %q", got)
	}
	if got := Normalize("café", NFD); got != decomposed {
		t.Errorf("NFD = %q", got)
	}
	if got := Normalize("ﬁ", NFKC); got != "fi" { // ligature ﬁ
		t.Errorf("NFKC = %q", got)
	}
}

func TestConvert(t *testing.T) {
	in := strings.NewReader("café") // UTF-8, decomposed
	var out bytes.Buffer
	if err := Convert(&out, in, "utf-8", "iso-8859-1", NFC); err != nil {
		t.Fatal(err)
	}
	if want := []byte{'c', 'a', 'f', 0xE9}; !bytes.Equal(out.Bytes(), want) {
		t.Fatalf("Convert = %x, want %x", out.Bytes(), want)
	}
}

func TestParseForm(t *testing.T) {
	if f, err := ParseForm("nfkd"); err != nil || f != NFKD {
		t.Fatalf("ParseForm(nfkd) = %v, %v", f, err)
	}
	if _, err := ParseForm("bogus"); err == nil {
		t.Fatal("expected error")
	}
}
