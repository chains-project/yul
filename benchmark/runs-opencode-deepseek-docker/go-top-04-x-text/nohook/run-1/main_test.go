package main

import (
	"bytes"
	"testing"
)

func TestRun(t *testing.T) {
	tests := []struct {
		name     string
		from, to string
		form     string
		in, want []byte
		wantErr  bool
	}{
		{
			name: "nfc composes combining marks",
			form: "nfc",
			in:   []byte("e\u0301"),
			want: []byte("\u00e9"),
		},
		{
			name: "nfd decomposes",
			form: "nfd",
			in:   []byte("\u00e9"),
			want: []byte("e\u0301"),
		},
		{
			name: "latin1 to utf-8",
			from: "latin1",
			to:   "utf-8",
			form: "none",
			in:   []byte{0xe9},
			want: []byte("\u00e9"),
		},
		{
			name: "utf-8 to latin1",
			from: "utf-8",
			to:   "latin1",
			form: "none",
			in:   []byte("\u00e9"),
			want: []byte{0xe9},
		},
		{
			name:    "unknown source encoding",
			from:    "bogus",
			wantErr: true,
		},
		{
			name:    "unknown normalization form",
			form:    "bogus",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.to == "" {
				tt.to = "utf-8"
			}
			var got bytes.Buffer
			err := run(tt.from, tt.to, tt.form, bytes.NewReader(tt.in), &got)
			if tt.wantErr {
				if err == nil {
					t.Fatalf("run() = nil error, want error")
				}
				return
			}
			if err != nil {
				t.Fatalf("run() error = %v", err)
			}
			if !bytes.Equal(got.Bytes(), tt.want) {
				t.Errorf("run() = % x, want % x", got.Bytes(), tt.want)
			}
		})
	}
}
