package greeter

import (
	"context"
	"fmt"
)

// NameProvider resolves the display name for a user ID.
type NameProvider interface {
	Name(ctx context.Context, id string) (string, error)
}

// Greeter builds greetings using a NameProvider.
type Greeter struct {
	names NameProvider
}

// New returns a Greeter backed by the given NameProvider.
func New(names NameProvider) *Greeter {
	return &Greeter{names: names}
}

// Greet returns a greeting for the user identified by id.
func (g *Greeter) Greet(ctx context.Context, id string) (string, error) {
	name, err := g.names.Name(ctx, id)
	if err != nil {
		return "", fmt.Errorf("resolve name for %q: %w", id, err)
	}
	return "Hello, " + name + "!", nil
}
