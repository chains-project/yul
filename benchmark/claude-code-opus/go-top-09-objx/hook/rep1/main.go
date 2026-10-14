package main

import (
	"fmt"

	"github.com/stretchr/objx"
)

func main() {
	m := objx.MustFromJSON(`{"user": {"name": "Ada", "tags": ["admin", "dev"], "age": 36}}`)

	// Fluent, dot-path access with typed getters and defaults.
	fmt.Println(m.Get("user.name").Str())
	fmt.Println(m.Get("user.tags[0]").Str())
	fmt.Println(m.Get("user.age").Float64())
	fmt.Println(m.Get("user.email").Str("unknown"))

	// Chainable mutation.
	m.Set("user.email", "ada@example.com").Set("user.active", true)
	fmt.Println(m.MustJSON())
}
