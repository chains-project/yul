package main

import (
	"fmt"

	"github.com/stretchr/objx"
)

func main() {
	m := objx.MustFromJSON(`{"user":{"name":"Ada","tags":["admin","dev"]}}`)

	// Read nested values with dot/array notation and typed accessors.
	fmt.Println(m.Get("user.name").Str())
	fmt.Println(m.Get("user.tags[0]").Str())
	fmt.Println(m.Get("user.age").Int(42)) // default when missing

	// Chainable mutation.
	m.Set("user.email", "ada@example.com").Set("active", true)
	fmt.Println(m.MustJSON())
}
