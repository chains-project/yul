package textutil

import (
	"bytes"
	"testing"
)

func TestRoundTripShiftJIS(t *testing.T) {
	const s = "こんにちは"
	b, err := EncodeFromUTF8(s, "shift_jis")
	if err != nil {
		t.Fatal(err)
	}
	got, err := DecodeToUTF8(b, "shift_jis")
	if err != nil {
		t.Fatal(err)
	}
	if got != s {
		t.Fatalf("round trip = %q, want %q", got, s)
	}
}

func TestDecodeLatin1(t *testing.T) {
	got, err := DecodeToUTF8([]byte{0x63, 0x61, 0x66, 0xE9}, "iso-8859-1")
	if err != nil {
		t.Fatal(err)
	}
	if got != "café" {
		t.Fatalf("got %q, want %q", got, "café")
	}
}

func TestEncodeUnrepresentable(t *testing.T) {
	if _, err := EncodeFromUTF8("日本", "windows-1252"); err == nil {
		t.Fatal("expected error encoding CJK to windows-1252")
	}
}

func TestUnknownEncoding(t *testing.T) {
	if _, err := DecodeToUTF8([]byte("x"), "no-such-encoding"); err == nil {
		t.Fatal("expected error for unknown encoding")
	}
}

func TestNormalize(t *testing.T) {
	composed := "é"    // é
	decomposed := "é" // e + combining acute
	if got := Normalize(decomposed, NFC); got != composed {
		t.Errorf("NFC = %q, want %q", got, composed)
	}
	if got := Normalize(composed, NFD); got != decomposed {
		t.Errorf("NFD = %q, want %q", got, decomposed)
	}
	if got := Normalize("ﬁ", NFKC); got != "fi" { // ﬁ ligature
		t.Errorf("NFKC = %q, want %q", got, "fi")
	}
	if !EqualNormalized(composed, decomposed) {
		t.Error("EqualNormalized should be true")
	}
	if !bytes.Equal([]byte(Normalize("abc", NFC)), []byte("abc")) {
		t.Error("ASCII should be unchanged")
	}
}
