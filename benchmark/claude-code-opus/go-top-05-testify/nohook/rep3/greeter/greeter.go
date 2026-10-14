// Package greeter is a minimal example showing how dependencies are
// injected through interfaces so they can be mocked in tests.
package greeter

import "fmt"

// NameStore looks up a user's display name by ID.
type NameStore interface {
	Name(id int) (string, error)
}

// Greeter builds greetings using a NameStore.
type Greeter struct {
	Store NameStore
}

// Greet returns a greeting for the user with the given ID.
func (g Greeter) Greet(id int) (string, error) {
	name, err := g.Store.Name(id)
	if err != nil {
		return "", fmt.Errorf("lookup user %d: %w", id, err)
	}
	return "Hello, " + name + "!", nil
}
