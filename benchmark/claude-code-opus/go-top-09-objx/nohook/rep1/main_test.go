package main

import (
	"testing"

	"github.com/stretchr/objx"
)

func TestFluentAccess(t *testing.T) {
	m := objx.New(map[string]interface{}{
		"user": map[string]interface{}{"name": "Ada"},
	})

	if got := m.Get("user.name").Str(); got != "Ada" {
		t.Fatalf("user.name = %q, want %q", got, "Ada")
	}
	if got := m.Get("user.missing").Str("default"); got != "default" {
		t.Fatalf("default = %q, want %q", got, "default")
	}

	m.Set("user.lang", "en").Set("count", 2)
	if got := m.Get("user.lang").Str(); got != "en" {
		t.Fatalf("user.lang = %q, want %q", got, "en")
	}
	if got := m.Get("count").Int(); got != 2 {
		t.Fatalf("count = %d, want 2", got)
	}
}
