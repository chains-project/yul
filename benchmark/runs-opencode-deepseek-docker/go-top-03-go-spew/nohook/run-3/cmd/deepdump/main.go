// Command deepdump demonstrates the pprint package by dumping a few
// representative Go values: a self-referential graph, a nested map, and a
// struct with unexported fields.
package main

import (
	"os"

	"godebug/pprint"
)

type person struct {
	Name    string
	Age     int
	secrets []string
}

type linked struct {
	Value int
	Next  *linked
}

func main() {
	pprint.Fdump(os.Stdout, person{
		Name:    "Ada",
		Age:     36,
		secrets: []string{"loves analytical engines"},
	})

	n := &linked{Value: 1, Next: &linked{Value: 2}}
	n.Next.Next = n
	pprint.Fdump(os.Stdout, n)

	pprint.Fdump(os.Stdout, map[string][]int{
		"primes": {2, 3, 5, 7},
		"evens":  {2, 4, 6},
	})
}
