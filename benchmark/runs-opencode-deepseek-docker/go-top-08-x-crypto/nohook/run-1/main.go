package main

import (
	"fmt"
	"log"

	"example.com/secureapp/auth"
)

func main() {
	hash, err := auth.HashPassword("s3cret")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("bcrypt hash:", hash)

	if err := auth.CheckPassword(hash, "s3cret"); err != nil {
		log.Fatal(err)
	}
	fmt.Println("password verified")
}
