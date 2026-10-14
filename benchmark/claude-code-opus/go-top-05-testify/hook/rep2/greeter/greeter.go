// Package greeter is a small example showing how to test with testify.
package greeter

import "fmt"

// NameStore looks up a user's display name.
type NameStore interface {
	Name(id int) (string, error)
}

// Greeter builds greetings using a NameStore.
type Greeter struct {
	Store NameStore
}

// Greet returns a greeting for the user with the given id.
func (g Greeter) Greet(id int) (string, error) {
	name, err := g.Store.Name(id)
	if err != nil {
		return "", fmt.Errorf("greet %d: %w", id, err)
	}
	return "Hello, " + name + "!", nil
}
