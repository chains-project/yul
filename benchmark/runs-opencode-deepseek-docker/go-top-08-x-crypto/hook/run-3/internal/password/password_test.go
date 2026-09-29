package password

import (
	"errors"
	"testing"
)

func TestHashVerifyRoundTrip(t *testing.T) {
	hash, err := Hash("correct horse battery staple")
	if err != nil {
		t.Fatalf("Hash: %v", err)
	}
	if hash == "correct horse battery staple" {
		t.Fatal("hash must not equal the plaintext")
	}
	if err := Verify(hash, "correct horse battery staple"); err != nil {
		t.Fatalf("Verify: %v", err)
	}
}

func TestVerifyRejectsWrongPassword(t *testing.T) {
	hash, err := Hash("correct horse battery staple")
	if err != nil {
		t.Fatalf("Hash: %v", err)
	}
	if err := Verify(hash, "wrong password"); !errors.Is(err, ErrMismatchedHashAndPassword) {
		t.Fatalf("expected ErrMismatchedHashAndPassword, got %v", err)
	}
}

func TestHashUsesUniqueSalt(t *testing.T) {
	first, err := Hash("same password")
	if err != nil {
		t.Fatalf("Hash: %v", err)
	}
	second, err := Hash("same password")
	if err != nil {
		t.Fatalf("Hash: %v", err)
	}
	if first == second {
		t.Fatal("hashes of the same password must differ due to salting")
	}
}
