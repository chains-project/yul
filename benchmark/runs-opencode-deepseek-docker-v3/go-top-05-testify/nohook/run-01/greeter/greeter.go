package greeter

import (
	"errors"
	"fmt"
)

var ErrNotFound = errors.New("name not found")

type NameStore interface {
	Lookup(id string) (string, error)
}

type Greeter struct {
	store NameStore
}

func New(store NameStore) *Greeter {
	return &Greeter{store: store}
}

func (g *Greeter) Greet(id string) (string, error) {
	name, err := g.store.Lookup(id)
	if err != nil {
		return "", fmt.Errorf("lookup %q: %w", id, err)
	}
	return "Hello, " + name + "!", nil
}
