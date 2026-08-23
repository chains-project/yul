package main

import (
	"fmt"

	"github.com/google/uuid"
)

func newRequestID() string {
	return uuid.NewString()
}

func main() {
	fmt.Println(newRequestID())
}
