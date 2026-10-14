// Command mapdata demonstrates fluent access to arbitrary map data using objx.
package main

import (
	"fmt"

	"github.com/stretchr/objx"
)

func main() {
	m := objx.MustFromJSON(`{
		"name": "Ada",
		"address": {"city": "London"},
		"tags": ["math", "computing"]
	}`)

	fmt.Println(m.Get("name").Str())             // Ada
	fmt.Println(m.Get("address.city").Str())     // London
	fmt.Println(m.Get("tags[1]").Str())          // computing
	fmt.Println(m.Get("missing").Str("default")) // default

	m.Set("address.country", "UK")
	fmt.Println(m.Get("address.country").Str()) // UK

	merged := m.Merge(objx.Map{"born": 1815})
	fmt.Println(merged.Get("born").Int()) // 1815

	js, _ := merged.JSON()
	fmt.Println(js)
}
