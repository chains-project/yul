package textconv

import "testing"

func TestDecodeWindows1252(t *testing.T) {
	// 0xE9 is 'é' in Windows-1252.
	got, err := Decode([]byte{0xE9}, "windows-1252")
	if err != nil {
		t.Fatalf("Decode: %v", err)
	}
	if got != "é" {
		t.Fatalf("Decode = %q, want %q", got, "é")
	}
}

func TestConvertRoundTrip(t *testing.T) {
	const want = "hello, 世界"
	data, err := Encode(want, "utf-16le")
	if err != nil {
		t.Fatalf("Encode: %v", err)
	}
	got, err := Decode(data, "utf-16le")
	if err != nil {
		t.Fatalf("Decode: %v", err)
	}
	if got != want {
		t.Fatalf("round trip = %q, want %q", got, want)
	}
}

func TestNormalize(t *testing.T) {
	// "é" as e + combining acute accent (NFD) normalizes to the precomposed
	// form under NFC.
	const decomposed = "e\u0301"
	got, err := Normalize(decomposed, "nfc")
	if err != nil {
		t.Fatalf("Normalize: %v", err)
	}
	if got != "\u00e9" {
		t.Fatalf("Normalize = %q, want %q", got, "\u00e9")
	}
}

func TestNormalizeUnknownForm(t *testing.T) {
	if _, err := Normalize("x", "NFX"); err == nil {
		t.Fatal("expected error for unknown form")
	}
}

func TestUnsupportedEncoding(t *testing.T) {
	if _, err := Decode(nil, "klingon"); err == nil {
		t.Fatal("expected error for unsupported encoding")
	}
}
