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
	hash, err := hashPassword("correct horse battery staple")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("hash:", hash)
	fmt.Println("match:", checkPassword("correct horse battery staple", hash))
}
