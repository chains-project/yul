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

	err = bcrypt.CompareHashAndPassword(hash, []byte("correct horse battery staple"))
	fmt.Println("password valid:", err == nil)
}
