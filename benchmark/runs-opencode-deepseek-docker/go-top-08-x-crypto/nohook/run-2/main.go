package main

import (
	"fmt"
	"os"

	"example.com/app/auth"
)

func main() {
	password := "correct horse battery staple"
	if len(os.Args) > 1 {
		password = os.Args[1]
	}

	hash, err := auth.HashPassword(password)
	if err != nil {
		fmt.Fprintln(os.Stderr, "hash:", err)
		os.Exit(1)
	}
	fmt.Println("hash:", hash)

	ok, err := auth.CheckPassword(password, hash)
	if err != nil {
		fmt.Fprintln(os.Stderr, "check:", err)
		os.Exit(1)
	}
	fmt.Println("password valid:", ok)

	ok, err = auth.CheckPassword("wrong password", hash)
	if err != nil {
		fmt.Fprintln(os.Stderr, "check:", err)
		os.Exit(1)
	}
	fmt.Println("wrong password valid:", ok)
}
