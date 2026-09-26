package main

import "github.com/davecgh/go-spew/spew"

type Address struct {
	City string
	Zip  string
}

type Person struct {
	Name    string
	Age     int
	Tags    []string
	Address *Address
	Meta    map[string]interface{}
}

func main() {
	p := &Person{
		Name: "Ada Lovelace",
		Age:  36,
		Tags: []string{"mathematician", "programmer"},
		Address: &Address{
			City: "London",
			Zip:  "SW1A",
		},
		Meta: map[string]interface{}{
			"active": true,
			"score":  42.5,
		},
	}

	spew.Dump(p)
}
