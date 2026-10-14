// Package greeter is a small example showing how to structure code so that
// its dependencies can be mocked in tests.
package greeter

import (
	"errors"
	"fmt"
)

// NameStore looks up a user's display name by ID.
type NameStore interface {
	Name(id int) (string, error)
}

// ErrInvalidID is returned when a non-positive ID is requested.
var ErrInvalidID = errors.New("greeter: invalid id")

// Greeter builds greetings using a NameStore.
type Greeter struct {
	store NameStore
}

// New returns a Greeter backed by store.
func New(store NameStore) *Greeter {
	return &Greeter{store: store}
}

// Greet returns a greeting for the user with the given ID.
func (g *Greeter) Greet(id int) (string, error) {
	if id <= 0 {
		return "", ErrInvalidID
	}
	name, err := g.store.Name(id)
	if err != nil {
		return "", fmt.Errorf("greeter: lookup %d: %w", id, err)
	}
	return "Hello, " + name + "!", nil
}
