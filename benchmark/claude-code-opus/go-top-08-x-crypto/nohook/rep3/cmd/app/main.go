package main

import (
	"fmt"
	"log"

	"example.com/app/internal/password"
)

func main() {
	h, err := password.Hash("s3cret")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("hash:", h)
	fmt.Println("verify:", password.Verify(h, "s3cret") == nil)
}
