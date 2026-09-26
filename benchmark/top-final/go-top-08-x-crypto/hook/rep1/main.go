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
	fmt.Println("hash:", string(hash))

	err = bcrypt.CompareHashAndPassword(hash, password)
	fmt.Println("match:", err == nil)
}
