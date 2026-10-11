package main

import (
	"fmt"
	"log"

	"golang.org/x/crypto/bcrypt"
)

func main() {
	password := []byte("correct horse battery staple")

	hash, err := bcrypt.GenerateFromPassword(password, bcrypt.DefaultCost)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("hash: %s\n", hash)

	if err := bcrypt.CompareHashAndPassword(hash, password); err != nil {
		log.Fatal("password mismatch: ", err)
	}
	fmt.Println("password verified")
}
