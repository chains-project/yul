package textconv

import "testing"

func TestRoundTripLatin1(t *testing.T) {
	b, err := Encode("café", "iso-8859-1")
	if err != nil {
		t.Fatal(err)
	}
	if len(b) != 4 || b[3] != 0xE9 {
		t.Fatalf("unexpected bytes: % x", b)
	}
	s, err := Decode(b, "latin1")
	if err != nil {
		t.Fatal(err)
	}
	if s != "café" {
		t.Fatalf("got %q", s)
	}
}

func TestEncodeUnrepresentable(t *testing.T) {
	if _, err := Encode("日本", "iso-8859-1"); err == nil {
		t.Fatal("expected error")
	}
}

func TestShiftJIS(t *testing.T) {
	b, err := Encode("日本語", "shift_jis")
	if err != nil {
		t.Fatal(err)
	}
	s, err := Decode(b, "shift_jis")
	if err != nil || s != "日本語" {
		t.Fatalf("got %q, %v", s, err)
	}
}

func TestNormalize(t *testing.T) {
	decomposed := "é" // e + combining acute
	if got := Normalize(decomposed, NFC); got != "é" {
		t.Fatalf("NFC: got %q", got)
	}
	if got := Normalize("é", NFD); got != decomposed {
		t.Fatalf("NFD: got %q", got)
	}
	if got := Normalize("ﬁ", NFKC); got != "fi" { // ﬁ ligature
		t.Fatalf("NFKC: got %q", got)
	}
}
