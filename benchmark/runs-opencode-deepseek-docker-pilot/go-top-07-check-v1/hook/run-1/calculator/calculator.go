package calculator

import "errors"

// ErrDivideByZero is returned when a division by zero is attempted.
var ErrDivideByZero = errors.New("calculator: division by zero")

// Calculator is a tiny stateful service used to demonstrate gocheck suites.
type Calculator struct {
	history []string
}

// New returns an empty Calculator ready for use.
func New() *Calculator { return &Calculator{} }

// Add returns a+b and records the operation.
func (c *Calculator) Add(a, b int) int {
	c.history = append(c.history, "add")
	return a + b
}

// Divide returns a/b and records the operation.
func (c *Calculator) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	c.history = append(c.history, "divide")
	return a / b, nil
}

// History returns a copy of the operations recorded so far.
func (c *Calculator) History() []string {
	out := make([]string, len(c.history))
	copy(out, c.history)
	return out
}
