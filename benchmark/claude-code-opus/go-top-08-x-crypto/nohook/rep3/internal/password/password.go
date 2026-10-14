// Package password provides password hashing and verification using bcrypt.
package password

import (
	"errors"

	"golang.org/x/crypto/bcrypt"
)

// Cost is the bcrypt work factor used for new hashes.
const Cost = 12

// ErrMismatch is returned when a password does not match its hash.
var ErrMismatch = errors.New("password: mismatch")

// Hash returns a bcrypt hash of the given password.
func Hash(plain string) (string, error) {
	h, err := bcrypt.GenerateFromPassword([]byte(plain), Cost)
	if err != nil {
		return "", err
	}
	return string(h), nil
}

// Verify reports whether plain matches the stored bcrypt hash.
func Verify(hash, plain string) error {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(plain))
	if errors.Is(err, bcrypt.ErrMismatchedHashAndPassword) {
		return ErrMismatch
	}
	return err
}
