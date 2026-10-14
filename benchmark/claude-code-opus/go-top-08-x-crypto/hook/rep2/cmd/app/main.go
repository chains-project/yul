package main

import (
	"fmt"
	"log"

	"golang.org/x/crypto/bcrypt"
)

func main() {
	hash, err := bcrypt.GenerateFromPassword([]byte("s3cret"), bcrypt.DefaultCost)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("hash:", string(hash))

	if err := bcrypt.CompareHashAndPassword(hash, []byte("s3cret")); err != nil {
		log.Fatal("password mismatch: ", err)
	}
	fmt.Println("password verified")
}
