package main

import (
	"testing"

	"github.com/stretchr/objx"
)

func TestFluentAccess(t *testing.T) {
	m := objx.New(map[string]interface{}{
		"a": map[string]interface{}{"b": 1},
	})
	m.Set("a.c.d", "x")

	if got := m.Get("a.b").Int(); got != 1 {
		t.Fatalf("a.b = %d, want 1", got)
	}
	if got := m.Get("a.c.d").Str(); got != "x" {
		t.Fatalf("a.c.d = %q, want x", got)
	}
}
