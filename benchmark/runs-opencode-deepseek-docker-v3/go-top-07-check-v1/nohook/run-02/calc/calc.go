package calc

import (
	"errors"
	"fmt"
)

var ErrDivideByZero = errors.New("division by zero")

type Calculator struct {
	history []string
}

func New() *Calculator {
	return &Calculator{}
}

func (c *Calculator) Add(a, b int) int {
	c.record(fmt.Sprintf("%d + %d", a, b))
	return a + b
}

func (c *Calculator) Subtract(a, b int) int {
	c.record(fmt.Sprintf("%d - %d", a, b))
	return a - b
}

func (c *Calculator) Multiply(a, b int) int {
	c.record(fmt.Sprintf("%d * %d", a, b))
	return a * b
}

func (c *Calculator) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	c.record(fmt.Sprintf("%d / %d", a, b))
	return a / b, nil
}

func (c *Calculator) History() []string {
	return append([]string(nil), c.history...)
}

func (c *Calculator) record(op string) {
	c.history = append(c.history, op)
}
