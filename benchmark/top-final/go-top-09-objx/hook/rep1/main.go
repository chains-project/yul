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
		"tags": []interface{}{"admin", "staff"},
	}

	name := m.Get("name").Str("unknown")
	city := m.Get("address.city").Str("unknown")

	m.Set("age", 30)

	fmt.Println(name, city, m.Get("age").Int(), m.Get("tags").MustInterSlice())
}
