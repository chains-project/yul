package main

import (
	"fmt"
	"log"

	"golang.org/x/crypto/bcrypt"
)

func main() {
	const password = "correct horse battery staple"

	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		log.Fatalf("hash password: %v", err)
	}
	fmt.Printf("hash: %s\n", hash)

	if err := bcrypt.CompareHashAndPassword(hash, []byte(password)); err != nil {
		log.Fatalf("password did not match: %v", err)
	}
	fmt.Println("password verified")
}
