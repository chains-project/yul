package password

import (
	"errors"
	"testing"
)

func TestHashAndVerify(t *testing.T) {
	h, err := Hash("correct horse battery staple")
	if err != nil {
		t.Fatal(err)
	}
	if err := Verify(h, "correct horse battery staple"); err != nil {
		t.Fatalf("expected match, got %v", err)
	}
	if err := Verify(h, "wrong"); !errors.Is(err, ErrMismatch) {
		t.Fatalf("expected ErrMismatch, got %v", err)
	}
}
