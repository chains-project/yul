package password

import "testing"

func TestHashAndVerify(t *testing.T) {
	hash, err := Hash("correct horse battery staple")
	if err != nil {
		t.Fatalf("Hash: %v", err)
	}
	if !Verify(hash, "correct horse battery staple") {
		t.Fatal("Verify rejected the correct password")
	}
	if Verify(hash, "wrong password") {
		t.Fatal("Verify accepted an incorrect password")
	}
}
