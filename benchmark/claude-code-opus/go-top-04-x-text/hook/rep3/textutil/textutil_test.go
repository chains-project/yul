package textutil

import (
	"testing"

	"golang.org/x/text/unicode/norm"
)

func TestRoundTripLatin1(t *testing.T) {
	const s = "café"
	b, err := EncodeFromUTF8(s, "iso-8859-1")
	if err != nil {
		t.Fatal(err)
	}
	if len(b) != 4 {
		t.Fatalf("expected 4 bytes in Latin-1, got %d", len(b))
	}
	got, err := DecodeToUTF8(b, "iso-8859-1")
	if err != nil {
		t.Fatal(err)
	}
	if got != s {
		t.Fatalf("got %q, want %q", got, s)
	}
}

func TestDecodeShiftJIS(t *testing.T) {
	got, err := DecodeToUTF8([]byte{0x93, 0xfa, 0x96, 0x7b}, "shift_jis")
	if err != nil {
		t.Fatal(err)
	}
	if got != "日本" {
		t.Fatalf("got %q, want %q", got, "日本")
	}
}

func TestEncodeUnrepresentable(t *testing.T) {
	if _, err := EncodeFromUTF8("日本", "iso-8859-1"); err == nil {
		t.Fatal("expected error encoding CJK to Latin-1")
	}
}

func TestUnknownEncoding(t *testing.T) {
	if _, err := Lookup("not-a-charset"); err == nil {
		t.Fatal("expected error")
	}
}

func TestNormalize(t *testing.T) {
	composed := "é"    // é
	decomposed := "é" // e + combining acute
	if Normalize(decomposed, norm.NFC) != composed {
		t.Error("NFC did not compose")
	}
	if Normalize(composed, norm.NFD) != decomposed {
		t.Error("NFD did not decompose")
	}
	if Normalize("ﬁ", norm.NFKC) != "fi" { // ﬁ ligature
		t.Error("NFKC did not fold ligature")
	}
	if !Equal(composed, decomposed) {
		t.Error("expected canonical equivalence")
	}
}
