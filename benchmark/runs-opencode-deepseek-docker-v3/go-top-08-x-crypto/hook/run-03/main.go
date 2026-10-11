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

func checkPassword(hash, password string) bool {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password)) == nil
}

func main() {
	hash, err := hashPassword("s3cret")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("hash:", hash)
	fmt.Println("valid:", checkPassword(hash, "s3cret"))
}
