package main

import (
	"testing"

	"github.com/stretchr/objx"
)

func TestFluentAccess(t *testing.T) {
	m := objx.New(map[string]interface{}{
		"user": map[string]interface{}{
			"name":  "Ada",
			"roles": []interface{}{"admin", "dev"},
		},
	})

	if got := m.Get("user.name").Str(); got != "Ada" {
		t.Errorf("user.name = %q, want %q", got, "Ada")
	}
	if got := m.Get("user.roles[0]").Str(); got != "admin" {
		t.Errorf("user.roles[0] = %q, want %q", got, "admin")
	}
	if got := m.Get("user.age").Int(42); got != 42 {
		t.Errorf("user.age default = %d, want 42", got)
	}

	m.Set("user.email", "ada@example.com")
	if !m.Has("user.email") {
		t.Error("expected user.email to be set")
	}
}
