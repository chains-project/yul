// Package auth provides password hashing helpers.
package auth

import (
	"errors"

	"golang.org/x/crypto/bcrypt"
)

// Cost is the bcrypt work factor used for new hashes.
const Cost = 12

// ErrMismatch is returned when a password does not match its hash.
var ErrMismatch = errors.New("auth: password does not match")

// HashPassword returns a bcrypt hash of password.
// bcrypt only uses the first 72 bytes; longer inputs return an error.
func HashPassword(password string) (string, error) {
	h, err := bcrypt.GenerateFromPassword([]byte(password), Cost)
	if err != nil {
		return "", err
	}
	return string(h), nil
}

// CheckPassword reports whether password matches hash.
func CheckPassword(hash, password string) error {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	if errors.Is(err, bcrypt.ErrMismatchedHashAndPassword) {
		return ErrMismatch
	}
	return err
}
