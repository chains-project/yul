package mapfluent_test

import (
	"fmt"

	"mapfluent"
)

func Example() {
	doc := mapfluent.New(map[string]interface{}{
		"user": map[string]interface{}{
			"name": "Ada",
			"langs": []interface{}{
				"go", "c",
			},
		},
	})

	// Read deeply nested values and convert them to Go types.
	name := doc.GetPath("user.name").String()
	first := doc.GetPath("user.langs[0]").String()

	// Mutate in place; every call returns the same Map for chaining.
	doc.SetPath("user.active", true).
		SetPath("user.name", "Ada Lovelace").
		DeletePath("user.langs")

	fmt.Println(name, first)
	fmt.Println(doc.GetPath("user.name").String(), doc.GetPath("user.active").Bool())
	fmt.Println(doc.HasPath("user.langs"))

	// Output:
	// Ada go
	// Ada Lovelace true
	// false
}

func ExampleFromJSON() {
	doc, err := mapfluent.FromJSON([]byte(`{"a":{"b":[10,20,30]}}`))
	if err != nil {
		fmt.Println("error:", err)
		return
	}

	fmt.Println(doc.GetPath("a.b[2]").Int())
	fmt.Println(doc.GetPath("a.b").Len())
	fmt.Println(doc.GetPath("a.missing.deep").IntOr(-1))

	// Output:
	// 30
	// 3
	// -1
}
