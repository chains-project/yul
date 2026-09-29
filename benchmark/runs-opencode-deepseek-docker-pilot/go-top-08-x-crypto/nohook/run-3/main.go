package main

import (
	"errors"
	"fmt"

	"golang.org/x/crypto/bcrypt"
)

func HashPassword(password string) (string, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hash), nil
}

func CheckPassword(hash, password string) error {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
}

func main() {
	hash, err := HashPassword("correct horse battery staple")
	if err != nil {
		panic(err)
	}
	fmt.Println("hash:", hash)

	if err := CheckPassword(hash, "correct horse battery staple"); err != nil {
		panic(err)
	}
	fmt.Println("password matches")

	if err := CheckPassword(hash, "wrong password"); !errors.Is(err, bcrypt.ErrMismatchedHashAndPassword) {
		panic("expected mismatch")
	}
	fmt.Println("wrong password rejected")
}
