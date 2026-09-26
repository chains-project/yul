package main

import (
	"fmt"
	"log"

	"golang.org/x/crypto/bcrypt"
)

func main() {
	hash, err := bcrypt.GenerateFromPassword([]byte("correct horse battery staple"), bcrypt.DefaultCost)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(hash))

	if err := bcrypt.CompareHashAndPassword(hash, []byte("correct horse battery staple")); err != nil {
		log.Fatal(err)
	}

	fmt.Println("password verified")
}
