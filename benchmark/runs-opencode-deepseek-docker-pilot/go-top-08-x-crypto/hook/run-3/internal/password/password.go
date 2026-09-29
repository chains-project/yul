package password

import (
	"errors"

	"golang.org/x/crypto/bcrypt"
)

var ErrMismatchedHashAndPassword = errors.New("password: hash and password do not match")

func Hash(plaintext string) (string, error) {
	hashed, err := bcrypt.GenerateFromPassword([]byte(plaintext), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hashed), nil
}

func Verify(hash, plaintext string) error {
	if err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(plaintext)); err != nil {
		if errors.Is(err, bcrypt.ErrMismatchedHashAndPassword) {
			return ErrMismatchedHashAndPassword
		}
		return err
	}
	return nil
}
