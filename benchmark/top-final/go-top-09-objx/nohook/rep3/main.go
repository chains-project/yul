package main

import (
	"fmt"

	"github.com/stretchr/objx"
)

func main() {
	data := objx.Map{
		"name": "Ada",
		"address": map[string]interface{}{
			"city": "London",
		},
		"tags": []interface{}{"engineer", "pioneer"},
	}

	city := data.Get("address.city").Str("unknown")
	tag := data.Get("tags[0]").Str("")

	fmt.Printf("name=%s city=%s tag=%s\n", data.Get("name").Str(), city, tag)
}
