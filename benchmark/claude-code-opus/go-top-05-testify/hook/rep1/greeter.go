// Package project is the root package of the module.
package project

import "fmt"

// NameStore looks up a user's display name by ID.
type NameStore interface {
	Name(id int) (string, error)
}

// Greet returns a greeting for the user with the given ID.
func Greet(s NameStore, id int) (string, error) {
	name, err := s.Name(id)
	if err != nil {
		return "", fmt.Errorf("greet user %d: %w", id, err)
	}
	return "Hello, " + name + "!", nil
}
