package main

import (
	"fmt"
	"log"

	"example.com/app/internal/auth"
)

func main() {
	hash, err := auth.HashPassword("s3cret")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("hash:", hash)
	fmt.Println("match:", auth.CheckPassword(hash, "s3cret") == nil)
}
