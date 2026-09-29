// Package greeter builds time-of-day greetings. It exists to demonstrate the
// test tooling configured for this module: testify for assertions and gomock
// for generated mocks.
package greeter

import "context"

// Clock reports the current hour of the day in the range [0, 23].
//
//go:generate go tool mockgen -source=greeter.go -destination=mock_clock_test.go -package=greeter
type Clock interface {
	Hour(ctx context.Context) (int, error)
}

// Greeter produces greetings based on the time reported by its Clock.
type Greeter struct {
	clock Clock
}

// New returns a Greeter backed by clock.
func New(clock Clock) *Greeter {
	return &Greeter{clock: clock}
}

// Greet returns a time-appropriate greeting for name.
func (g *Greeter) Greet(ctx context.Context, name string) (string, error) {
	hour, err := g.clock.Hour(ctx)
	if err != nil {
		return "", err
	}

	switch {
	case hour < 12:
		return "Good morning, " + name + "!", nil
	case hour < 18:
		return "Good afternoon, " + name + "!", nil
	default:
		return "Good evening, " + name + "!", nil
	}
}
