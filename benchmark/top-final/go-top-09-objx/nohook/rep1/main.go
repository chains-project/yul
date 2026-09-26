package main

import (
	"fmt"

	"github.com/stretchr/objx"
)

func main() {
	m := objx.Map{
		"name": "Ada",
		"address": map[string]interface{}{
			"city": "London",
		},
	}

	name := m.Get("name").Str("unknown")
	city := m.Get("address.city").Str("unknown")

	fmt.Printf("%s lives in %s\n", name, city)
}
