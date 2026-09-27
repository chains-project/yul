package auth

import "testing"

func TestHashPasswordAndCheckPassword(t *testing.T) {
	const password = "correct horse battery staple"

	hash, err := HashPassword(password)
	if err != nil {
		t.Fatalf("HashPassword: %v", err)
	}
	if hash == password {
		t.Fatal("password was stored in plaintext")
	}

	if err := CheckPassword(hash, password); err != nil {
		t.Fatalf("CheckPassword with correct password: %v", err)
	}
	if err := CheckPassword(hash, "wrong password"); err == nil {
		t.Fatal("CheckPassword with wrong password: expected an error")
	}
}
