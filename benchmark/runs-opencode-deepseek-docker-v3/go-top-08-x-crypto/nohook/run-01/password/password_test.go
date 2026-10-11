package password

import "testing"

func TestHashVerify(t *testing.T) {
	hash, err := Hash("s3cr3t")
	if err != nil {
		t.Fatalf("Hash: %v", err)
	}
	if hash == "s3cr3t" {
		t.Fatal("hash must not equal plaintext")
	}
	if err := Verify(hash, "s3cr3t"); err != nil {
		t.Fatalf("Verify correct password: %v", err)
	}
	if err := Verify(hash, "wrong"); err != ErrMismatch {
		t.Fatalf("Verify wrong password = %v, want ErrMismatch", err)
	}
}
