package dynmap

import (
	"reflect"
	"testing"
)

func TestParsePath(t *testing.T) {
	tests := []struct {
		path string
		want []token
	}{
		{"", nil},
		{"a", []token{{kind: keyToken, key: "a"}}},
		{"a.b.c", []token{
			{kind: keyToken, key: "a"},
			{kind: keyToken, key: "b"},
			{kind: keyToken, key: "c"},
		}},
		{"users[0].name", []token{
			{kind: keyToken, key: "users"},
			{kind: indexToken, index: 0},
			{kind: keyToken, key: "name"},
		}},
		{"matrix[1][2]", []token{
			{kind: keyToken, key: "matrix"},
			{kind: indexToken, index: 1},
			{kind: indexToken, index: 2},
		}},
		{"[3]", []token{{kind: indexToken, index: 3}}},
		{"a[ 4 ]", []token{
			{kind: keyToken, key: "a"},
			{kind: indexToken, index: 4},
		}},
	}
	for _, tt := range tests {
		got, err := parsePath(tt.path)
		if err != nil {
			t.Errorf("parsePath(%q) error: %v", tt.path, err)
			continue
		}
		if !reflect.DeepEqual(got, tt.want) {
			t.Errorf("parsePath(%q) = %#v; want %#v", tt.path, got, tt.want)
		}
	}
}

func TestParsePathErrors(t *testing.T) {
	for _, path := range []string{"a[", "a[x]", "a[-1]", "a[]"} {
		if _, err := parsePath(path); err == nil {
			t.Errorf("parsePath(%q) = nil error; want error", path)
		}
	}
}
