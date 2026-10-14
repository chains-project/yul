// Package greeter is a small example showing how to structure code so it can
// be tested with testify's assert, require, and mock packages.
package greeter

import (
	"errors"
	"fmt"
)

// ErrEmptyName is returned when Greet is called with an empty name.
var ErrEmptyName = errors.New("greeter: name must not be empty")

// NameStore looks up display names by user ID. Depending on this interface
// rather than a concrete type lets tests substitute a mock.
type NameStore interface {
	DisplayName(userID string) (string, error)
}

// Greeter builds greetings for users.
type Greeter struct {
	store NameStore
}

// New returns a Greeter backed by store.
func New(store NameStore) *Greeter {
	return &Greeter{store: store}
}

// Greet returns a greeting for the user with the given ID.
func (g *Greeter) Greet(userID string) (string, error) {
	name, err := g.store.DisplayName(userID)
	if err != nil {
		return "", fmt.Errorf("greeter: looking up %q: %w", userID, err)
	}
	if name == "" {
		return "", ErrEmptyName
	}
	return "Hello, " + name + "!", nil
}
