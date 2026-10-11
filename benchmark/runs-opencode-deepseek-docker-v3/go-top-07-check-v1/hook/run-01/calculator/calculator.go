package calculator

import "errors"

var ErrDivideByZero = errors.New("division by zero")

type Calculator struct {
	history []int
}

func New() *Calculator {
	return &Calculator{}
}

func (c *Calculator) Add(a, b int) int {
	result := a + b
	c.history = append(c.history, result)
	return result
}

func (c *Calculator) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	result := a / b
	c.history = append(c.history, result)
	return result, nil
}

func (c *Calculator) History() []int {
	return append([]int(nil), c.history...)
}

func (c *Calculator) Reset() {
	c.history = nil
}
