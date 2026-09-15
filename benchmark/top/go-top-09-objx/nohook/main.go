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
		"tags": []string{"admin", "staff"},
	}

	fmt.Println(m.Get("name").Str())
	fmt.Println(m.Get("address.city").Str("unknown"))
	fmt.Println(m.Get("tags").StrSlice())
	fmt.Println(m.Has("missing"))

	m.Set("address.zip", "SW1A 1AA")
	fmt.Println(m.Get("address.zip").Str())
}
