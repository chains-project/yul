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

	fmt.Println(m.Get("name").Str())
	fmt.Println(m.Get("address.city").Str("unknown"))
	fmt.Println(m.Set("address.city", "Paris").Get("address.city").Str())
}
