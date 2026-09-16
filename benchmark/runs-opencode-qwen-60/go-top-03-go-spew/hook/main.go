package main

import (
	"fmt"
	"os"

	"github.com/davecgh/go-spew/spew"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <data_structure>\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "\nExample: %s map[string]int{1: 2, 3: 4}\n", os.Args[0])
		os.Exit(1)
	}

	fmt.Println("Dumper Output:")
	fmt.Println("==============")

	// Print the command line arguments as a sample data structure
	fmt.Println("\n1. All command line arguments:")
	spew.Dump(os.Args[1:])

	// Print environment variables as a sample data structure
	env := make(map[string]string)
	for _, e := range os.Environ() {
		for i, c := range e {
			if c == '=' {
				env[e[:i]] = e[i+1:]
				break
			}
		}
	}
	fmt.Println("\n2. Environment variables (first 5):")
	count := 0
	for k, v := range env {
		if count >= 5 {
			break
		}
		fmt.Printf("  %s: %s\n", k, v)
		count++
	}

	// Demonstrate deep pretty printing with a complex structure
	fmt.Println("\n3. Complex data structure:")
	type Nested struct {
		Name    string
		Values  []int
		Options map[string]interface{}
	}
	type Complex struct {
		ID      int
		Nested  Nested
		Items   []map[string]interface{}
	}

	complexData := Complex{
		ID: 42,
		Nested: Nested{
			Name:   "example",
			Values: []int{1, 2, 3, 4, 5},
			Options: map[string]interface{}{
				"debug": true,
				"count": 10,
				"tags":  []string{"a", "b", "c"},
			},
		},
		Items: []map[string]interface{}{
			{"id": 1, "value": "first"},
			{"id": 2, "value": "second"},
		},
	}
	spew.Dump(complexData)

	fmt.Println("\n4. Formatted output:")
	spew.Dump(env)
}