package main

import (
	"fmt"

	"github.com/stretchr/objx"
)

func main() {
	data := objx.MustFromJSON(`{
		"user": {"name": "Ada", "tags": ["admin", "dev"], "age": 36}
	}`)

	// Read nested values with dot/array paths and typed accessors.
	fmt.Println(data.Get("user.name").Str())
	fmt.Println(data.Get("user.tags[0]").Str())
	fmt.Println(data.Get("user.age").Int())
	fmt.Println(data.Get("user.missing").Str("default"))

	// Chainable writes, including creating intermediate maps.
	data.Set("user.address.city", "London").Set("active", true)

	out, _ := data.JSON()
	fmt.Println(out)
}
