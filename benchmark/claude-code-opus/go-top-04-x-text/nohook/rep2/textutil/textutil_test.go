package textutil

import (
	"testing"

	"golang.org/x/text/unicode/norm"
)

func TestRoundTrip(t *testing.T) {
	for _, enc := range []string{"windows-1252", "iso-8859-1", "shift_jis", "utf-16le"} {
		in := "café"
		if enc == "shift_jis" {
			in = "こんにちは"
		}
		b, err := FromUTF8(in, enc)
		if err != nil {
			t.Fatalf("%s: encode: %v", enc, err)
		}
		got, err := ToUTF8(b, enc)
		if err != nil {
			t.Fatalf("%s: decode: %v", enc, err)
		}
		if got != in {
			t.Errorf("%s: round trip = %q, want %q", enc, got, in)
		}
	}
}

func TestUnknownEncoding(t *testing.T) {
	if _, err := ToUTF8([]byte("x"), "not-an-encoding"); err == nil {
		t.Error("expected error for unknown encoding")
	}
}

func TestNormalize(t *testing.T) {
	composed := "é"    // é
	decomposed := "é" // e + combining acute
	if got := Normalize(decomposed, norm.NFC); got != composed {
		t.Errorf("NFC = %q, want %q", got, composed)
	}
	if got := Normalize(composed, norm.NFD); got != decomposed {
		t.Errorf("NFD = %q, want %q", got, decomposed)
	}
	if got := Normalize("ﬁ", norm.NFKC); got != "fi" {
		t.Errorf("NFKC(ﬁ) = %q, want %q", got, "fi")
	}
}

func TestParseForm(t *testing.T) {
	if f, err := ParseForm("nfkd"); err != nil || f != norm.NFKD {
		t.Errorf("ParseForm(nfkd) = %v, %v", f, err)
	}
	if _, err := ParseForm("bogus"); err == nil {
		t.Error("expected error for bogus form")
	}
}
