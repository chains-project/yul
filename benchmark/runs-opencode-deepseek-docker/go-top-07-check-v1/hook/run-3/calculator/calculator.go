package calculator

import "errors"

// ErrDivideByZero is returned when a division by zero is attempted.
var ErrDivideByZero = errors.New("calculator: division by zero")

// Calculator performs basic arithmetic and records every operation it runs.
type Calculator struct {
	history []string
}

// New returns an empty Calculator ready for use.
func New() *Calculator {
	return &Calculator{}
}

// Add returns the sum of a and b.
func (c *Calculator) Add(a, b int) int {
	c.history = append(c.history, "add")
	return a + b
}

// Sub returns the difference of a and b.
func (c *Calculator) Sub(a, b int) int {
	c.history = append(c.history, "sub")
	return a - b
}

// Mul returns the product of a and b.
func (c *Calculator) Mul(a, b int) int {
	c.history = append(c.history, "mul")
	return a * b
}

// Div returns the quotient of a and b, or ErrDivideByZero when b is 0.
func (c *Calculator) Div(a, b int) (int, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	c.history = append(c.history, "div")
	return a / b, nil
}

// History returns the operations performed so far, in order.
func (c *Calculator) History() []string {
	return c.history
}
