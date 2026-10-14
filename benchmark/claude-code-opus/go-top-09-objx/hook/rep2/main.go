package main

import (
	"fmt"
	"log"

	"github.com/stretchr/objx"
)

func main() {
	// Parse arbitrary JSON into an objx.Map (a map[string]interface{}).
	m, err := objx.FromJSON(`{
		"user": {
			"name": "Ada",
			"roles": ["admin", "dev"],
			"address": {"city": "London"}
		}
	}`)
	if err != nil {
		log.Fatal(err)
	}

	// Dot/bracket paths with typed, defaulted accessors.
	fmt.Println(m.Get("user.name").Str())
	fmt.Println(m.Get("user.roles[0]").Str())
	fmt.Println(m.Get("user.age").Int(42)) // missing -> default

	// Chainable mutation.
	m.Set("user.address.zip", "NW1").
		Set("user.active", true)

	// Navigate into sub-maps.
	addr := m.Get("user.address").ObjxMap()
	fmt.Println(addr.Get("city").Str(), addr.Get("zip").Str())

	// Wrap an existing map[string]interface{}.
	raw := map[string]interface{}{"count": 3}
	fmt.Println(objx.New(raw).Get("count").Int())

	out, _ := m.JSON()
	fmt.Println(out)
}
