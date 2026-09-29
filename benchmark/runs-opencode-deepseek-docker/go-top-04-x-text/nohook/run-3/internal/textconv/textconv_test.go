package textconv

import (
	"bytes"
	"io"
	"testing"
)

func TestConvertLatin1ToUTF8(t *testing.T) {
	got, err := Convert([]byte{0xE9}, "iso-8859-1", "utf-8")
	if err != nil {
		t.Fatalf("Convert: %v", err)
	}
	if want := "é"; string(got) != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

func TestConvertRoundTripShiftJIS(t *testing.T) {
	const text = "日本語のテキスト"
	sjis, err := Convert([]byte(text), "utf-8", "shift_jis")
	if err != nil {
		t.Fatalf("encode shift_jis: %v", err)
	}
	if bytes.Equal(sjis, []byte(text)) {
		t.Fatal("expected shift_jis bytes to differ from UTF-8")
	}
	back, err := Convert(sjis, "shift_jis", "utf-8")
	if err != nil {
		t.Fatalf("decode shift_jis: %v", err)
	}
	if string(back) != text {
		t.Fatalf("round trip got %q, want %q", back, text)
	}
}

func TestConvertUnknownCharset(t *testing.T) {
	if _, err := Convert([]byte("x"), "not-a-charset", "utf-8"); err == nil {
		t.Fatal("expected error for unknown charset")
	}
}

func TestReaderWriter(t *testing.T) {
	const text = "Grüße"
	var buf bytes.Buffer
	w, err := Writer(&buf, "iso-8859-1")
	if err != nil {
		t.Fatalf("Writer: %v", err)
	}
	if _, err := w.Write([]byte(text)); err != nil {
		t.Fatalf("write: %v", err)
	}

	r, err := Reader(bytes.NewReader(buf.Bytes()), "iso-8859-1")
	if err != nil {
		t.Fatalf("Reader: %v", err)
	}
	out, err := io.ReadAll(r)
	if err != nil {
		t.Fatalf("read: %v", err)
	}
	if string(out) != text {
		t.Fatalf("got %q, want %q", out, text)
	}
}

func TestNormalize(t *testing.T) {
	decomposed := "e\u0301"
	if got := Normalize(decomposed, NFC); got != "\u00e9" {
		t.Fatalf("NFC got %q, want %q", got, "\u00e9")
	}
	if got := Normalize("\u00e9", NFD); got != decomposed {
		t.Fatalf("NFD got %q, want %q", got, decomposed)
	}
	if got := Normalize("\uFB01", NFKC); got != "fi" {
		t.Fatalf("NFKC got %q, want %q", got, "fi")
	}
	if got := Normalize("\uFB01", NFC); got != "\uFB01" {
		t.Fatalf("NFC got %q, want unchanged %q", got, "\uFB01")
	}
}

func TestIsNormalized(t *testing.T) {
	if !IsNormalized("\u00e9", NFC) {
		t.Fatal("é is already NFC")
	}
	if IsNormalized("e\u0301", NFC) {
		t.Fatal("decomposed sequence is not NFC")
	}
}

func TestParseForm(t *testing.T) {
	for _, tc := range []struct {
		in   string
		want Form
	}{
		{"nfc", NFC},
		{" NFD ", NFD},
		{"NFKC", NFKC},
		{"nfkd", NFKD},
	} {
		got, err := ParseForm(tc.in)
		if err != nil {
			t.Fatalf("ParseForm(%q): %v", tc.in, err)
		}
		if got != tc.want {
			t.Fatalf("ParseForm(%q) = %v, want %v", tc.in, got, tc.want)
		}
	}
	if _, err := ParseForm("nope"); err == nil {
		t.Fatal("expected error for bad form")
	}
}
