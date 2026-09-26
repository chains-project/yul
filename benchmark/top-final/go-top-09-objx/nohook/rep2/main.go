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

	m.Set("address.zip", "SW1A").Set("age", 30)
	fmt.Println(m.Get("age").Int())
}
