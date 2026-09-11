package main

import (
	"fmt"
	"log"

	"golang.org/x/crypto/bcrypt"
)

func hashPassword(password string) (string, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hash), nil
}

func checkPassword(password, hash string) bool {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password)) == nil
}

func main() {
	password := "correct horse battery staple"

	hash, err := hashPassword(password)
	if err != nil {
		log.Fatalf("failed to hash password: %v", err)
	}
	fmt.Println("hash:", hash)

	fmt.Println("matches correct password:", checkPassword(password, hash))
	fmt.Println("matches wrong password:", checkPassword("wrong password", hash))
}
