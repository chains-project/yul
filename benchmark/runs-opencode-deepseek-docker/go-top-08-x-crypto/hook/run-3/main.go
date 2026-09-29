package main

import (
	"fmt"
	"log"

	"example.com/cryptoapp/internal/password"
)

func main() {
	hash, err := password.Hash("correct horse battery staple")
	if err != nil {
		log.Fatalf("hash password: %v", err)
	}
	fmt.Println("hash:", hash)

	if err := password.Verify(hash, "correct horse battery staple"); err != nil {
		log.Fatalf("verify correct password: %v", err)
	}
	if err := password.Verify(hash, "wrong password"); err == nil {
		log.Fatal("verify wrong password: expected an error")
	}
	fmt.Println("password verified")
}
