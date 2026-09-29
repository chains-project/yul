package main

import (
	"fmt"
	"log"

	"cryptoapp/password"
)

func main() {
	const plain = "correct horse battery staple"

	hash, err := password.Hash(plain)
	if err != nil {
		log.Fatalf("hash: %v", err)
	}
	fmt.Println("hash:", hash)

	if !password.Verify(hash, plain) {
		log.Fatal("verification failed for correct password")
	}
	if password.Verify(hash, "wrong password") {
		log.Fatal("verification succeeded for wrong password")
	}

	fmt.Println("password verified")
}
