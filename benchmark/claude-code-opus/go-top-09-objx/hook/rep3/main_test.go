package main

import (
	"testing"

	"github.com/stretchr/objx"
)

func TestObjxAccess(t *testing.T) {
	m := objx.Map{"a": map[string]interface{}{"b": []interface{}{"x", "y"}}}

	if got := m.Get("a.b[1]").Str(); got != "y" {
		t.Fatalf("a.b[1] = %q, want %q", got, "y")
	}

	m.Set("a.c", 7).Set("d", "z")
	if got := m.Get("a.c").Int(); got != 7 {
		t.Fatalf("a.c = %d, want 7", got)
	}
	if !m.Has("d") {
		t.Fatal("expected key d to exist")
	}
}
