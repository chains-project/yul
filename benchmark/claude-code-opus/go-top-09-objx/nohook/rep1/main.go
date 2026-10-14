package main

import (
	"fmt"

	"github.com/stretchr/objx"
)

func main() {
	// Wrap arbitrary JSON-like data.
	m := objx.MustFromJSON(`{
		"name": "Ada",
		"address": {"city": "London"},
		"tags": ["math", "computing"]
	}`)

	// Fluent, path-based reads with typed accessors and defaults.
	fmt.Println(m.Get("name").Str())
	fmt.Println(m.Get("address.city").Str())
	fmt.Println(m.Get("tags[1]").Str())
	fmt.Println(m.Get("age").Int(36)) // missing key -> default

	// Chainable writes (intermediate maps are created as needed).
	m.Set("address.country", "UK").Set("active", true)

	// Plain map[string]interface{} still available.
	var raw map[string]interface{} = m.Value().MSI()
	fmt.Println(raw["active"], m.Get("address.country").Str())
}
