package textutil

import (
	"bytes"
	"testing"
)

func TestConvertRoundTrip(t *testing.T) {
	latin1 := []byte{'c', 'a', 'f', 0xE9} // "café" in ISO-8859-1
	s, err := DecodeToUTF8(latin1, "iso-8859-1")
	if err != nil {
		t.Fatal(err)
	}
	if s != "café" {
		t.Fatalf("got %q, want %q", s, "café")
	}
	back, err := EncodeFromUTF8(s, "iso-8859-1")
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(back, latin1) {
		t.Fatalf("round trip mismatch: %x", back)
	}
}

func TestEncodeUnrepresentable(t *testing.T) {
	if _, err := EncodeFromUTF8("日本", "iso-8859-1"); err == nil {
		t.Fatal("expected error for unrepresentable characters")
	}
}

func TestUnknownEncoding(t *testing.T) {
	if _, err := DecodeToUTF8([]byte("x"), "not-an-encoding"); err == nil {
		t.Fatal("expected error for unknown encoding")
	}
}

func TestNormalize(t *testing.T) {
	composed := "é"    // é
	decomposed := "é" // e + combining acute
	if got := Normalize(decomposed, NFC); got != composed {
		t.Errorf("NFC: got %q, want %q", got, composed)
	}
	if got := Normalize(composed, NFD); got != decomposed {
		t.Errorf("NFD: got %q, want %q", got, decomposed)
	}
	if got := Normalize("ﬁ", NFKC); got != "fi" { // ligature ﬁ
		t.Errorf("NFKC: got %q, want %q", got, "fi")
	}
}
