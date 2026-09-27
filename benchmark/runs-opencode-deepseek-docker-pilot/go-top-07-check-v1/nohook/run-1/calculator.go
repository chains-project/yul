package calc

import "errors"

var ErrDivideByZero = errors.New("division by zero")

type Calculator struct {
	history []string
}

func (c *Calculator) Add(a, b int) int {
	c.history = append(c.history, "add")
	return a + b
}

func (c *Calculator) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	c.history = append(c.history, "divide")
	return a / b, nil
}

func (c *Calculator) History() []string {
	return c.history
}
