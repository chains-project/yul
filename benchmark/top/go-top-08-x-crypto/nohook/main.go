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
		log.Fatal(err)
	}
	fmt.Println("hash:", hash)

	fmt.Println("correct password matches:", checkPassword(password, hash))
	fmt.Println("wrong password matches:", checkPassword("wrong password", hash))
}
