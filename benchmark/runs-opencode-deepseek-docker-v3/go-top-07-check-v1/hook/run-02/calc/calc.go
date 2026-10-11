package calc

import "errors"

type Calculator struct {
	history []int
}

func (c *Calculator) Add(a, b int) int {
	result := a + b
	c.history = append(c.history, result)
	return result
}

func (c *Calculator) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	result := a / b
	c.history = append(c.history, result)
	return result, nil
}

func (c *Calculator) History() []int {
	out := make([]int, len(c.history))
	copy(out, c.history)
	return out
}
